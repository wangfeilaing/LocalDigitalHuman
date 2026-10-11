from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any


def serializable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serializable(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(child) for child in value]
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def main() -> int:
    if len(sys.argv) != 2:
        print("LOCALDH_ERROR=缺少任务配置", flush=True)
        return 2

    config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    module_root = Path(config.pop("module_root")).resolve()
    runtime = config.pop("runtime", {})
    ffmpeg_dir = Path(config.pop(
        "ffmpeg_dir", r"C:\Program Files\aigc-human\resources\ffmpeg\bin"
    ))
    os.chdir(module_root)
    sys.path.insert(0, str(module_root))
    venv = module_root / "venv"
    runtime_paths = [
        ffmpeg_dir,
        venv / "Library" / "bin",
        venv / "DLLs",
        venv,
        venv / "Scripts",
        venv / "Lib" / "site-packages" / "torch" / "lib",
        venv / "Lib" / "site-packages" / "onnxruntime" / "capi",
    ]
    existing_path = os.environ.get("PATH", "")
    os.environ["PATH"] = os.pathsep.join(
        [str(path) for path in runtime_paths if path.exists()] + [existing_path]
    )
    if hasattr(os, "add_dll_directory"):
        dll_handles = [os.add_dll_directory(str(path)) for path in runtime_paths if path.is_dir()]

    os.environ["BATCH_SIZE"] = str(runtime.get("batch_size", 6))
    os.environ["PARALLEL_FACE_DETECT"] = "1" if runtime.get("parallel_face_detect") else "0"
    os.environ["PARALLEL_THREADS"] = str(runtime.get("parallel_threads", 4))

    # Configure the module's singleton before its compiled entry point is imported.
    try:
        from y_utils.config import GlobalConfig

        runtime_config = GlobalConfig.instance()
        runtime_config.batch_size = int(runtime.get("batch_size", 6))
        runtime_config.parallel_face_detect = int(bool(runtime.get("parallel_face_detect")))
        runtime_config.parallel_threads = int(runtime.get("parallel_threads", 4))
        runtime_config.face_cache_enable = int(bool(runtime.get("face_cache")))
        runtime_config.face_cache_dir = str(runtime.get("face_cache_dir") or "./face_cache")
        runtime_config.face_cache_show_log = 0
        Path(runtime_config.face_cache_dir).mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        print(f"LOCALDH_OPTIMIZATION_WARNING={exc}", flush=True)

    print("LOCALDH_STAGE=IMPORTING", flush=True)
    import main as digital_module

    print("LOCALDH_STAGE=READY", flush=True)
    result = digital_module.generateDigitalHuman(
        audio_file=config["audio_file"],
        video_file=config["video_file"],
        watermark=bool(config.get("watermark", False)),
        digital_auth=bool(config.get("digital_auth", False)),
        output_dir=config.get("output_dir"),
    )
    print("LOCALDH_RESULT=" + json.dumps(serializable(result), ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as exc:
        print("LOCALDH_ERROR=" + str(exc), flush=True)
        traceback.print_exc()
        raise
    raise SystemExit(exit_code)
