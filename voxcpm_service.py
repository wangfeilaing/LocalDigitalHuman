"""VoxCPM local voice service for the Local Digital Human workbench.

Runs inside the dedicated VoxCPM virtual environment and exposes the same
HTTP contract as the legacy local voice service (port 8001):

    GET  /health   -> {"model_loaded": true, "engine": "voxcpm"}
    POST /generate -> {"code": 200, "msg": "success", "data": {"output_path": ...}}

Generation modes (chosen automatically from the payload):
    prompt_audio + prompt_text -> ultimate cloning (continuation + reference)
    prompt_audio only          -> reference-based cloning
    neither                    -> plain text-to-speech

The optional ``speed`` value (0.5-2.0 from the workbench UI) is applied with an
ffmpeg atempo post-pass because VoxCPM has no native speaking-rate parameter.
``cfg_value`` (1.0-5.0) and ``inference_timesteps`` (4-30) are also accepted
from the workbench UI; both default to 2.0 / 10.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = int(os.environ.get("VOXCPM_PORT", "8002"))
MODEL_DIR = os.environ.get(
    "VOXCPM_MODEL_DIR", r"C:\Users\w1227\voxcpm\models\VoxCPM2"
)
FFMPEG_EXE = Path(os.environ.get(
    "LOCAL_DH_FFMPEG_EXE",
    r"C:\Program Files\aigc-human\resources\ffmpeg\bin\ffmpeg.exe",
))

MODEL = None
MODEL_ERROR: str | None = None
GENERATE_LOCK = threading.Lock()


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def load_model() -> None:
    global MODEL, MODEL_ERROR
    try:
        import torch  # noqa: F401  (ensures CUDA initialises before the model)

        from voxcpm import VoxCPM

        log(f"正在加载 VoxCPM 模型：{MODEL_DIR}")
        started = time.time()
        MODEL = VoxCPM.from_pretrained(MODEL_DIR, load_denoiser=False)
        log(f"模型加载完成，用时 {time.time() - started:.1f} 秒")
    except Exception:
        MODEL_ERROR = traceback.format_exc(limit=3)
        log(f"模型加载失败：{MODEL_ERROR}")


def apply_speed(source: Path, speed: float) -> Path:
    if abs(speed - 1.0) < 1e-3:
        return source
    if not FFMPEG_EXE.is_file():
        log(f"没有找到 ffmpeg，跳过语速调整：{FFMPEG_EXE}")
        return source
    tempo = min(max(speed, 0.5), 2.0)
    adjusted = source.with_name(source.stem + "_atempo.wav")
    completed = subprocess.run(
        [
            str(FFMPEG_EXE), "-loglevel", "error", "-y",
            "-i", str(source),
            "-af", f"atempo={tempo:.3f}",
            "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
            str(adjusted),
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not adjusted.is_file() or adjusted.stat().st_size == 0:
        log(f"语速调整失败，使用原始速度：{completed.stderr[-200:]}")
        adjusted.unlink(missing_ok=True)
        return source
    return adjusted


def generate(payload: dict) -> Path:
    import soundfile as sf

    text = str(payload.get("text") or "").strip()
    if not text:
        raise ValueError("缺少要合成的文本。")
    prompt_audio = str(payload.get("prompt_audio_path") or "").strip()
    prompt_text = str(payload.get("prompt_text") or "").strip()
    output_path = Path(str(payload.get("output_path") or "").strip())
    if not output_path.name:
        raise ValueError("缺少输出路径。")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        speed = float(payload.get("speed") or 1.0)
    except (TypeError, ValueError):
        speed = 1.0
    try:
        cfg_value = min(5.0, max(1.0, float(payload.get("cfg_value", 2.0))))
    except (TypeError, ValueError):
        cfg_value = 2.0
    try:
        inference_timesteps = min(30, max(4, int(float(payload.get("inference_timesteps", 10)))))
    except (TypeError, ValueError):
        inference_timesteps = 10

    kwargs: dict = {"text": text, "cfg_value": cfg_value, "inference_timesteps": inference_timesteps}
    if prompt_audio and Path(prompt_audio).is_file():
        kwargs["reference_wav_path"] = prompt_audio
        if prompt_text:
            kwargs["prompt_wav_path"] = prompt_audio
            kwargs["prompt_text"] = prompt_text

    with GENERATE_LOCK:
        started = time.time()
        wav = MODEL.generate(**kwargs)
        raw_path = output_path.with_name(output_path.stem + "_raw.wav")
        sf.write(str(raw_path), wav, MODEL.tts_model.sample_rate, subtype="PCM_16")
        final = apply_speed(raw_path, speed)
        if final != output_path:
            final.replace(output_path)
        raw_path.unlink(missing_ok=True)
        log(f"合成完成：{len(text)} 字，用时 {time.time() - started:.1f} 秒 "
            f"(cfg={cfg_value}, timesteps={inference_timesteps}, speed={speed}) -> {output_path.name}")
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("VoxCPM 没有生成有效的音频文件。")
    return output_path


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format_string: str, *args) -> None:  # keep the log clean
        pass

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.rstrip("/") in {"", "/health"}:
            self.send_json({
                "model_loaded": MODEL is not None,
                "engine": "voxcpm",
                "error": MODEL_ERROR,
            })
        else:
            self.send_json({"code": 404, "msg": "not found"}, status=404)

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/generate":
            self.send_json({"code": 404, "msg": "not found"}, status=404)
            return
        if MODEL is None:
            self.send_json({"code": 503, "msg": MODEL_ERROR or "VoxCPM 模型还没有加载完成。"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            result = generate(payload)
            self.send_json({"code": 200, "msg": "success", "data": {"output_path": str(result)}})
        except Exception as exc:
            log(f"合成失败：{exc}\n{traceback.format_exc(limit=3)}")
            self.send_json({"code": 500, "msg": str(exc)})


def main() -> int:
    loader = threading.Thread(target=load_model, daemon=True)
    loader.start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    log(f"VoxCPM 声音服务已启动：http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
