from __future__ import annotations

import json
import mimetypes
import argparse
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import server  # noqa: E402


DEFAULT_TEST_TEXT = (
    "[thoughtful] 人这一生，真正重要的不是走得有多快，而是在每一次选择面前，"
    "都能听见自己内心的声音。[warm] 当你愿意相信自己，改变就已经开始了。"
)


def multipart_body(audio_path: Path, fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----LocalDigitalHuman{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode("ascii"),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
            value.encode("utf-8"),
            b"\r\n",
        ])
    content_type = mimetypes.guess_type(audio_path.name)[0] or "audio/mpeg"
    chunks.extend([
        f"--{boundary}\r\n".encode("ascii"),
        (
            f'Content-Disposition: form-data; name="audio"; '
            f'filename="{audio_path.name}"\r\n'
        ).encode("utf-8"),
        f"Content-Type: {content_type}\r\n\r\n".encode("ascii"),
        audio_path.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode("ascii"),
    ])
    return b"".join(chunks), boundary


def convert_voice(api_key: str, voice_id: str, source: Path, output: Path) -> Path:
    settings = {
        "stability": 0.75,
        "similarity_boost": 0.90,
        "style": 0.0,
        "use_speaker_boost": True,
    }
    body, boundary = multipart_body(source, {
        "model_id": "eleven_multilingual_sts_v2",
        "voice_settings": json.dumps(settings, ensure_ascii=False),
        "remove_background_noise": "false",
    })
    url = (
        "https://api.elevenlabs.io/v1/speech-to-speech/"
        f"{urllib.parse.quote(voice_id, safe='')}?output_format=mp3_44100_128"
    )
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "xi-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            output.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Voice Changer failed ({exc.code}): {detail[:500]}") from exc
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Voice Changer did not return valid audio.")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-file", type=Path)
    parser.add_argument("--label", default="V3双阶段测试")
    args = parser.parse_args()
    text = DEFAULT_TEST_TEXT
    if args.text_file:
        text = args.text_file.read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError("Test text is empty.")
    if not text.lstrip().startswith("["):
        text = f"[thoughtful] {text}"
    accounts = [item for item in server.load_elevenlabs_accounts() if item.get("status") == "ready"]
    if not accounts:
        raise RuntimeError("No ready ElevenLabs account.")
    account = accounts[0]
    api_key = server.unprotect_local_secret(str(account.get("secret") or ""))
    voice = next(
        (item for item in account.get("voices") or [] if "讲师A" in str(item.get("name") or "")),
        None,
    )
    if not voice:
        raise RuntimeError("Zhang Tingwei voice was not found in the synced account.")

    output_dir = server.DEFAULT_OUTPUT
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    label = server.output_title_stem(str(args.label or "V3双阶段测试"))
    v3_path = output_dir / f"{label}-V3 Natural原声-{stamp}.mp3"
    converted_path = output_dir / f"{label}-V3情感＋讲师A音色转换-{stamp}.mp3"
    voice_id = str(voice.get("voiceId") or "")

    server.generate_elevenlabs_voice(
        text,
        api_key,
        voice_id,
        v3_path,
        speed=0.98,
        model_id="eleven_v3",
        output_format="mp3_44100_128",
        settings={
            "stability": 0.50,
            "similarityBoost": 0.90,
            "style": 0.0,
            "speakerBoost": True,
        },
    )
    convert_voice(api_key, voice_id, v3_path, converted_path)
    print(json.dumps({
        "ok": True,
        "text": text,
        "v3": str(v3_path),
        "converted": str(converted_path),
        "v3Bytes": v3_path.stat().st_size,
        "convertedBytes": converted_path.stat().st_size,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
