"""本地语音转写工具（FunASR SenseVoiceSmall，CPU 运行，不占显存）。

用法：python tools/transcribe.py <audio.wav>
输出：stdout 最后一行为 JSON {"ok": true, "text": "..."}，供 server.py 解析。
首次运行会从 ModelScope 下载模型（约 500MB）到 ~/.cache/modelscope。
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "缺少音频路径"}, ensure_ascii=True))
        return 1
    audio_path = sys.argv[1]
    try:
        from funasr import AutoModel
        from funasr.utils.postprocess_utils import rich_transcription_postprocess

        model = AutoModel(
            model="iic/SenseVoiceSmall",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cpu",
            disable_update=True,
        )
        result = model.generate(
            input=audio_path,
            cache={},
            language="zh",
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            merge_length_s=15,
        )
        raw = ""
        if result and isinstance(result, list):
            raw = str(result[0].get("text") or "")
        text = rich_transcription_postprocess(raw).strip()
        if not text:
            raise RuntimeError("没有识别到有效内容，请确认样本里包含清晰人声。")
        print(json.dumps({"ok": True, "text": text}, ensure_ascii=True))
        return 0
    except Exception as exc:  # noqa: BLE001 - 需要把任何失败透传给工作台
        print(json.dumps({"ok": False, "error": str(exc)[:300]}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
