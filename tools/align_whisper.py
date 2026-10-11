"""字幕对齐工具（faster-whisper large-v3-turbo 词级时间戳 + 文案锚定匹配）。

用法：python tools/align_whisper.py <request.json>
请求：{
    "ffmpeg": "ffmpeg.exe 路径（可选）",
    "model_dir": "CT2 模型目录（可选，默认 ModelScope 缓存路径）",
    "device": "cuda|cpu（可选，默认 cuda 失败回退 cpu）",
    "pairs": [{"audio": "part_00001.mp3", "text": "该段音频对应的文案"}, ...]
}
输出：stdout 最后一行 JSON（与 align_subtitles.py 完全相同的契约）
    {"ok": true, "segments": [{"charCount": 38, "timestamps": [[起ms, 止ms], ...]}, ...]}

原理：Whisper 只负责产出词级时间轴，字幕文案是我们自己的——把 Whisper 识别
文本的净字符流与文案净字符流做 difflib 锚定匹配：匹配块直接取 Whisper 的时间，
错字/多字/漏字块在两侧锚点间线性插值。因此识别错字（如数字写法、同音字）
不会污染对齐结果。整体匹配率过低时抛错，由工作台回退 FunASR 链路。
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_MODEL_DIR = (
    Path.home() / ".cache" / "modelscope" / "hub" / "models"
    / "pengzhendong" / "faster-whisper-large-v3-turbo"
)
MIN_MATCH_RATIO = 0.5   # 匹配块字符占比低于此值视为对齐不可靠
MIN_CHAR_MS = 10.0      # 单字符最小时长（后处理单调性修正用）


def clean_chars(text: str) -> str:
    return re.sub(r"[^\w一-鿿]+", "", text.lower())


def to_wav_16k(ffmpeg: str, audio: str, work_dir: Path) -> Path:
    """统一转成 16k 单声道 wav，避免 mp3 解码差异。"""
    source = Path(audio)
    if source.suffix.lower() == ".wav":
        return source
    target = work_dir / f"{source.stem}_16k.wav"
    completed = subprocess.run(
        [ffmpeg, "-loglevel", "error", "-y", "-i", str(source),
         "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(target)],
        capture_output=True, text=True, timeout=300,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not target.is_file():
        raise RuntimeError(f"音频转码失败：{completed.stderr[-200:]}")
    return target


def load_model(model_dir: str, device: str):
    from faster_whisper import WhisperModel

    if device == "cpu":
        return WhisperModel(model_dir, device="cpu", compute_type="int8")
    try:
        return WhisperModel(model_dir, device="cuda", compute_type="float16")
    except Exception as exc:  # noqa: BLE001 - 显存被占等情况回退 CPU
        print(f"CUDA 加载失败，回退 CPU int8：{exc}", file=sys.stderr, flush=True)
        return WhisperModel(model_dir, device="cpu", compute_type="int8")


def whisper_char_timeline(model, wav_path: Path) -> tuple[list[str], list[list[float]]]:
    """跑 Whisper，把词级时间戳摊平成识别文本的逐字时间轴。"""
    segments, _info = model.transcribe(
        str(wav_path),
        language="zh",
        task="transcribe",
        word_timestamps=True,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters={"threshold": 0.3, "min_silence_duration_ms": 400},
        beam_size=5,
    )
    chars: list[str] = []
    times: list[list[float]] = []
    for segment in segments:
        for word in (segment.words or []):
            cleaned = clean_chars(word.word)
            if not cleaned:
                continue
            start_ms = max(0.0, float(word.start) * 1000.0)
            end_ms = max(start_ms + MIN_CHAR_MS, float(word.end) * 1000.0)
            step = (end_ms - start_ms) / len(cleaned)
            for index, ch in enumerate(cleaned):
                chars.append(ch)
                times.append([start_ms + index * step, start_ms + (index + 1) * step])
    return chars, times


def anchor_map(known: str, rec_chars: list[str], rec_times: list[list[float]],
               duration_ms: float) -> list[list[float]]:
    """把识别侧逐字时间轴映射回文案净字符流。

    equal 块直接取识别时间；replace/insert/delete 块在两侧锚点间线性插值。
    """
    total = len(known)
    output: list[list[float]] = [[0.0, 0.0] for _ in range(total)]
    matched = 0
    matcher = difflib.SequenceMatcher(None, known, rec_chars, autojunk=False)
    opcodes = matcher.get_opcodes()

    def anchor_before(pos: int) -> float:
        """pos 之前最近的已确定时间（该字符的结束时间）。"""
        for i in range(pos - 1, -1, -1):
            if output[i][1] > 0:
                return output[i][1]
        return 0.0

    for tag, k1, k2, r1, r2 in opcodes:
        if tag == "equal":
            for offset in range(k2 - k1):
                output[k1 + offset] = list(rec_times[r1 + offset])
            matched += k2 - k1
            continue
        # 不对齐块：两侧锚点间线性插值
        count = k2 - k1
        if count <= 0:
            continue
        t0 = anchor_before(k1)
        if r2 > r1:
            # replace 块：识别错字的时间本身就是对的，直接用识别侧该块的时间区间
            t0 = max(t0, rec_times[r1][0])
            t1 = rec_times[r2 - 1][1]
        elif r2 < len(rec_times):
            # delete 块（漏识别）：右锚点是下一个识别词的开始时间
            t1 = rec_times[r2][0]
        else:
            t1 = None
        if t1 is None:
            t1 = duration_ms
        t1 = min(max(t1, t0 + MIN_CHAR_MS * count), duration_ms)  # 保底正向步长
        step = (t1 - t0) / count
        for j in range(count):
            output[k1 + j] = [t0 + j * step, t0 + (j + 1) * step]

    if total > 0 and matched / total < MIN_MATCH_RATIO:
        raise ValueError(f"Whisper 匹配率过低：{matched}/{total}，对齐结果不可信。")

    # 单调性修正：逐字保证 start >= 前字 end，end > start，且不超出音频范围
    fixed: list[list[float]] = []
    prev_end = 0.0
    for start, end in output:
        start = max(0.0, min(float(start), duration_ms))
        start = max(start, prev_end)
        end = max(float(end), start + MIN_CHAR_MS)
        end = min(end, duration_ms)
        if end <= start:
            end = min(duration_ms, start + MIN_CHAR_MS)
        fixed.append([start, end])
        prev_end = end
    return fixed


def align_pair(model, ffmpeg: str, audio: str, text: str, work_dir: Path) -> dict:
    import soundfile as sf

    wav_path = to_wav_16k(ffmpeg, audio, work_dir)
    samples, sample_rate = sf.read(str(wav_path), dtype="float32", always_2d=False)
    duration_ms = len(samples) / sample_rate * 1000.0

    known = clean_chars(text)
    if not known:
        raise ValueError("文案没有可对齐的有效字符。")
    rec_chars, rec_times = whisper_char_timeline(model, wav_path)
    if not rec_chars:
        raise ValueError("Whisper 没有产出任何词级时间戳。")
    timestamps = anchor_map(known, rec_chars, rec_times, duration_ms)
    return {"charCount": len(known), "timestamps": timestamps}


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "缺少请求文件"}, ensure_ascii=True))
        return 1
    try:
        request = json.loads(open(sys.argv[1], encoding="utf-8").read())
        pairs = request.get("pairs") or []
        if not pairs:
            raise ValueError("请求里没有要对齐的音频。")
        ffmpeg = str(request.get("ffmpeg") or "ffmpeg")
        model_dir = str(request.get("model_dir") or DEFAULT_MODEL_DIR)
        if not Path(model_dir).is_dir():
            raise RuntimeError(f"Whisper 模型目录不存在：{model_dir}")
        device = str(request.get("device") or "auto")

        model = load_model(model_dir, device)
        segments = []
        with tempfile.TemporaryDirectory(prefix="align_whisper_") as tmp:
            work_dir = Path(tmp)
            for pair in pairs:
                audio = str(pair.get("audio") or "")
                text = str(pair.get("text") or "").strip()
                if not audio or not text:
                    raise ValueError("对齐请求缺少音频或文本。")
                segments.append(align_pair(model, ffmpeg, audio, text, work_dir))
        print(json.dumps({"ok": True, "segments": segments}, ensure_ascii=True))
        return 0
    except Exception as exc:  # noqa: BLE001 - 任何失败都透传给工作台走回退
        print(json.dumps({"ok": False, "error": str(exc)[:300]}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
