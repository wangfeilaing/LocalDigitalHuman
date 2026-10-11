from __future__ import annotations

import cgi
import base64
import ctypes
from ctypes import wintypes
import json
import hashlib
import mimetypes
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    import jieba
except ImportError:  # Semantic subtitle splitting still has a safe fallback.
    jieba = None

try:
    import psutil
except ImportError:  # The app can still run without process sweeping.
    psutil = None


APP_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = int(os.environ.get("LOCAL_DH_PORT", "17860"))

# ---------------------------------------------------------------------------
# 安装布局与本地配置
#
# 外部组件路径一律按三级解析：环境变量 > local-config.json > 默认候选
# （安装目录内布局优先，旧机器的写死路径兜底）。精简安装包只需把组件
# 放进安装目录（runtime/、modules/）或写 local-config.json，不用改代码。
# ---------------------------------------------------------------------------
LOCAL_CONFIG_PATH = APP_DIR / "local-config.json"


def load_local_config() -> dict[str, Any]:
    try:
        data = json.loads(LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


LOCAL_CONFIG = load_local_config()


def config_text(key: str, env_name: str) -> str:
    return os.environ.get(env_name, "").strip() or str(LOCAL_CONFIG.get(key) or "").strip()


def config_path(key: str, env_name: str) -> Path | None:
    raw = config_text(key, env_name)
    return Path(raw) if raw else None


def first_existing_path(candidates: list[Path | None], fallback: Path) -> Path:
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return fallback


def default_output_dir() -> Path:
    override = config_path("defaultOutput", "LOCAL_DH_OUTPUT_DIR")
    if override:
        return override
    legacy = Path(r"D:\数字人视频输出")
    if legacy.anchor and Path(legacy.anchor).exists():
        return legacy
    return Path.home() / "Videos" / "数字人视频输出"


DEFAULT_OUTPUT = default_output_dir()
TEMP_DIR = APP_DIR / "temp"
LOG_DIR = APP_DIR / "logs"
DATA_DIR = APP_DIR / "data"
AVATAR_DIR = DATA_DIR / "avatars"
AVATAR_INDEX = AVATAR_DIR / "avatars.json"
VOICE_LIBRARY_DIR = DATA_DIR / "voices"
VOICE_INDEX = VOICE_LIBRARY_DIR / "voices.json"
ELEVENLABS_ACCOUNT_INDEX = DATA_DIR / "elevenlabs-accounts.json"
PERSON_INDEX = DATA_DIR / "persons.json"
MUSIC_LIBRARY_DIR = DATA_DIR / "music"
MUSIC_INDEX = MUSIC_LIBRARY_DIR / "music.json"
BROLL_DIR = DATA_DIR / "broll"
BROLL_INDEX = BROLL_DIR / "broll-index.json"
BROLL_EMBEDDING_CACHE = BROLL_DIR / "broll-embeddings.npz"
BROLL_MODEL_DIR = DATA_DIR / "models" / "bge-small-zh-v1.5"
BROLL_MATCHER = APP_DIR / "broll_matcher.py"
BROLL_UPLOAD_DIR = BROLL_DIR / "uploads"
BROLL_UPLOAD_THUMBNAIL_DIR = BROLL_DIR / "upload-thumbnails"
BROLL_CLASSIFIER_MODEL_DIR = DATA_DIR / "models" / "clip-vit-base-patch32"
BROLL_CLASSIFIER = APP_DIR / "broll_classifier.py"
FOLDER_PICKER_SCRIPT = APP_DIR / "tools" / "select-folder.ps1"
QUEUE_PATH = DATA_DIR / "task-queue.json"
MODEL_INPUT_DIR = DATA_DIR / "model-inputs"
UPLOAD_DIR = TEMP_DIR / "uploads"
VOICE_CHECKPOINT_DIR = TEMP_DIR / "voice-checkpoints"
FACE_CACHE_DIR = DATA_DIR / "face-cache"
CUSTOM_FONT_DIR = DATA_DIR / "fonts"
FFMPEG_DIR = first_existing_path(
    [
        config_path("ffmpegDir", "LOCAL_DH_FFMPEG_DIR"),
        APP_DIR / "runtime" / "ffmpeg" / "bin",
        Path(r"C:\Program Files\aigc-human\resources\ffmpeg\bin"),
    ],
    APP_DIR / "runtime" / "ffmpeg" / "bin",
)
FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_EXE = FFMPEG_DIR / "ffprobe.exe"
# 成片整体音量：用户反馈默认音量偏小，导出时统一放大 1/3（约 +2.5dB），限幅 -1dB 防破音
EXPORT_AUDIO_FILTER = "volume=1.333,alimiter=limit=0.891:level=false"
LOCAL_VOICE_SEGMENT_CHARS = 180
ELEVENLABS_SEGMENT_CHARS = 1200
LOCAL_VOICE_SEGMENT_RETRIES = 3
MODEL_BATCH_SIZE = int(config_text("modelBatchSize", "LOCAL_DH_MODEL_BATCH_SIZE") or 6)
GPU_MIN_FREE_MB = int(config_text("gpuMinFreeMB", "LOCAL_DH_GPU_MIN_FREE_MB") or 6500)
CHECKPOINT_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
TEXT_FONTS = {
    "dongfangdakai": "Alimama DongFangDaKai",
    "yahei": "Microsoft YaHei",
    "heiti": "SimHei",
    "songti": "SimSun",
    "kaiti": "KaiTi",
    "fangsong": "FangSong",
}
TEXT_SHADOWS = {
    "none": 0,
    "soft": 1,
    "standard": 2,
    "strong": 4,
}

# VoxCPM voice engine (optional; absent in the slim installer package).
VOXCPM_ROOT = first_existing_path(
    [
        config_path("voxcpmRoot", "LOCAL_DH_VOXCPM_ROOT"),
        APP_DIR / "runtime" / "voxcpm",
        Path(r"C:\Users\w1227\voxcpm"),
    ],
    config_path("voxcpmRoot", "LOCAL_DH_VOXCPM_ROOT") or APP_DIR / "runtime" / "voxcpm",
)
VOXCPM_PYTHON = VOXCPM_ROOT / "venv311" / "Scripts" / "python.exe"
VOXCPM_MODEL_DIR = VOXCPM_ROOT / "models" / "VoxCPM2"
VOXCPM_SERVICE = APP_DIR / "voxcpm_service.py"
TRANSCRIBE_SCRIPT = APP_DIR / "tools" / "transcribe.py"
ALIGN_SCRIPT = APP_DIR / "tools" / "align_subtitles.py"
WHISPER_ALIGN_SCRIPT = APP_DIR / "tools" / "align_whisper.py"
WHISPER_MODEL_DIR = first_existing_path(
    [
        config_path("whisperModelDir", "LOCAL_DH_WHISPER_MODEL_DIR"),
        DATA_DIR / "models" / "faster-whisper-large-v3-turbo",
        Path.home() / ".cache" / "modelscope" / "hub" / "models"
        / "pengzhendong" / "faster-whisper-large-v3-turbo",
    ],
    DATA_DIR / "models" / "faster-whisper-large-v3-turbo",
)
VOICE_ENGINES = {"v2": 8001, "voxcpm": 8002}
VOICE_ENGINE_NAMES = {"v2": "IndexTTS-2 · 本地免费", "voxcpm": "VoxCPM 2 · 本地免费"}

ELEVENLABS_DEFAULT_MODELS = [
    {
        "modelId": "eleven_multilingual_v2",
        "name": "Multilingual v2",
        "description": "成片优先，中文长文稳定、声音自然",
        "maxCharacters": 10000,
        "recommended": True,
        "supportsStyle": True,
        "supportsSpeakerBoost": True,
    },
    {
        "modelId": "eleven_v3",
        "name": "Eleven v3",
        "description": "情绪表现更丰富，适合强调语气的短内容",
        "maxCharacters": 5000,
        "recommended": False,
        "supportsStyle": False,
        "supportsSpeakerBoost": False,
    },
    {
        "modelId": "eleven_turbo_v2",
        "name": "Eleven Turbo v2",
        "description": "速度优先，适合批量任务和快速成片。",
        "maxCharacters": 30000,
        "recommended": False,
        "supportsStyle": True,
        "supportsSpeakerBoost": True,
    },
    {
        "modelId": "eleven_flash_v2_5",
        "name": "Flash v2.5",
        "description": "速度优先，适合批量生成和快速试听",
        "maxCharacters": 40000,
        "recommended": False,
        "supportsStyle": True,
        "supportsSpeakerBoost": True,
    },
]
ELEVENLABS_OUTPUT_FORMATS = [
    {"id": "mp3_44100_128", "name": "MP3 44.1kHz · 标准"},
    {"id": "mp3_44100_192", "name": "MP3 44.1kHz · 高码率"},
]
ELEVENLABS_OUTPUT_FORMAT_IDS = {item["id"] for item in ELEVENLABS_OUTPUT_FORMATS}
ELEVENLABS_GENERATION_MODES = [
    {
        "id": "multilingual_v2",
        "name": "Multilingual v2 · 音色稳定",
        "description": "中文长文稳定，优先保持本人音色。",
        "modelId": "eleven_multilingual_v2",
        "doublePass": False,
    },
    {
        "id": "v3",
        "name": "V3 · 情感优先",
        "description": "情绪和语气更丰富，音色可能比本人略有变化。",
        "modelId": "eleven_v3",
        "doublePass": False,
    },
    {
        "id": "turbo_v2",
        "name": "Eleven Turbo v2 · 快速输出",
        "description": "生成速度快；这个版本偏英文，中文优先使用 Multilingual v2 或结合版。",
        "modelId": "eleven_turbo_v2",
        "doublePass": False,
    },
    {
        "id": "v3_voice_match",
        "name": "V3情感＋本人音色",
        "description": "先用V3生成情感，再转换回目标音色；效果优先，会调用两次云端处理。",
        "modelId": "eleven_v3",
        "doublePass": True,
    },
]
ELEVENLABS_GENERATION_MODE_MAP = {
    item["id"]: item for item in ELEVENLABS_GENERATION_MODES
}

MODULE_CANDIDATES = [
    APP_DIR / "modules",
    Path(r"C:\Program Files\aigc-human\python-modules"),
    Path(r"E:\讲师A数字人\本地附加文件3.1.0完整版\python-modules"),
]

for directory in (
    DEFAULT_OUTPUT, TEMP_DIR, LOG_DIR, AVATAR_DIR, VOICE_LIBRARY_DIR,
    MUSIC_LIBRARY_DIR, BROLL_DIR, BROLL_UPLOAD_DIR, BROLL_UPLOAD_THUMBNAIL_DIR,
    MODEL_INPUT_DIR, UPLOAD_DIR, VOICE_CHECKPOINT_DIR,
    FACE_CACHE_DIR, CUSTOM_FONT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


def discover_modules_root() -> Path:
    configured = config_path("modulesRoot", "LOCAL_DH_MODULES_ROOT")
    candidates = ([configured] if configured else []) + MODULE_CANDIDATES
    # 口型 v2（hdModule）是核心组件；v1（humanModule）与本地声音模块在
    # 精简安装包里可以不存在，不再作为识别模块根目录的条件。
    for candidate in candidates:
        if (candidate / "hdModule").exists():
            return candidate
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


MODULES_ROOT = discover_modules_root()
STATE_LOCK = threading.RLock()
VOICE_LOCK = threading.RLock()
RUN_LOCK = threading.Lock()
AVATAR_LOCK = threading.RLock()
PERSON_LOCK = threading.RLock()
VOICE_LIBRARY_LOCK = threading.RLock()
ELEVENLABS_ACCOUNT_LOCK = threading.RLock()
MUSIC_LIBRARY_LOCK = threading.RLock()
BROLL_LOCK = threading.RLock()
QUEUE_LOCK = threading.RLock()
QUEUE_WAKE = threading.Event()


def log_unhandled_exception(where: str) -> None:
    """pythonw 下 stderr 被丢弃，线程崩溃必须落盘，否则队列假死无从排查。"""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with (LOG_DIR / "server-error.log").open("a", encoding="utf-8") as fh:
            fh.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {where}\n")
            fh.write(traceback.format_exc())
    except Exception:
        pass


def _thread_excepthook(args: "threading.ExceptHookArgs") -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with (LOG_DIR / "server-error.log").open("a", encoding="utf-8") as fh:
            thread_name = getattr(args.thread, "name", "?")
            fh.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] thread {thread_name} crashed\n")
            traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback, file=fh)
    except Exception:
        pass


threading.excepthook = _thread_excepthook
VOICE_WARMUP_LOCK = threading.Lock()
VOICE_PROCESS: subprocess.Popen[str] | None = None
VOICE_ENGINE: str | None = None
VOICE_LOG_HANDLE: Any = None
VOICE_LAST_USED = 0.0
QUEUE_ITEMS: list[dict[str, Any]] = []
QUEUE_SECRETS: dict[str, str] = {}
QUEUE_WORKER: threading.Thread | None = None
QUEUE_PAUSED = False
# 用户手动停止当前生成任务的信号：主任务在各阶段边界检查，
# 命中后杀掉子进程、释放声音服务显存，再按“已取消”落库。
MAIN_CANCEL = threading.Event()


class TaskCancelled(Exception):
    """用户手动停止当前生成任务。"""


def raise_if_main_cancelled() -> None:
    if MAIN_CANCEL.is_set():
        raise TaskCancelled("任务已手动停止。")


def initial_job(kind: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "id": None,
        "status": "idle",
        "progress": 0,
        "stage": "",
        "message": "",
        "error": None,
        "result": None,
        "cover": None,
        "audio": None,
        "outputDir": None,
        "segmentsTotal": 0,
        "segmentsDone": 0,
        "startedAt": None,
        "elapsedSeconds": 0,
        "estimatedSeconds": None,
        "log": [],
    }


JOBS = {
    "main": initial_job("main"),
    "preview": initial_job("preview"),
    "clone": initial_job("clone"),
    "setup": initial_job("setup"),
}


def snapshot_job(kind: str) -> dict[str, Any]:
    with STATE_LOCK:
        return json.loads(json.dumps(JOBS.get(kind, JOBS["main"]), ensure_ascii=False))


def reset_job(kind: str) -> str:
    job_id = uuid.uuid4().hex
    with STATE_LOCK:
        JOBS[kind] = initial_job(kind)
        JOBS[kind].update({"id": job_id, "status": "running", "startedAt": time.time()})
    return job_id


def update_job(kind: str, **changes: Any) -> None:
    with STATE_LOCK:
        JOBS[kind].update(changes)


def append_job_log(kind: str, line: str) -> None:
    clean = line.strip()
    if not clean:
        return
    with STATE_LOCK:
        JOBS[kind]["log"].append(clean)
        JOBS[kind]["log"] = JOBS[kind]["log"][-200:]


def save_queue_state() -> None:
    with QUEUE_LOCK:
        temporary = QUEUE_PATH.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(
                {"version": 3, "paused": QUEUE_PAUSED, "items": QUEUE_ITEMS},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        temporary.replace(QUEUE_PATH)


def load_queue_state() -> None:
    global QUEUE_ITEMS, QUEUE_PAUSED
    with QUEUE_LOCK:
        try:
            payload = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
            items = payload.get("items") if isinstance(payload, dict) else []
            QUEUE_ITEMS = items if isinstance(items, list) else []
            QUEUE_PAUSED = bool(payload.get("paused", False)) if isinstance(payload, dict) else False
        except (OSError, ValueError, TypeError):
            QUEUE_ITEMS = []
            QUEUE_PAUSED = False
        changed = False
        for item in QUEUE_ITEMS:
            if item.get("status") == "running":
                item["status"] = "pending"
                item["stage"] = "上次运行中断，等待自动继续"
                item["progress"] = 0
                changed = True
        if changed:
            save_queue_state()


def queue_is_busy() -> bool:
    with QUEUE_LOCK:
        return any(item.get("status") in {"pending", "running"} for item in QUEUE_ITEMS)


def assert_asset_not_used_by_queue(kind: str, asset_id: str) -> None:
    payload_key = {"avatar": "avatarId", "voice": "localVoiceId", "music": "musicId"}.get(kind)
    if not payload_key:
        return
    with QUEUE_LOCK:
        in_use = next(
            (
                item for item in QUEUE_ITEMS
                if item.get("status") in {"pending", "paused", "running"}
                and str((item.get("payload") or {}).get(payload_key) or "") == asset_id
            ),
            None,
        )
    if in_use is not None:
        raise ValueError(f"这项内容正在被队列任务“{in_use.get('title') or '未命名任务'}”使用，暂时不能删除。")


def queue_title(text: str, position: int) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    preview = compact[:24] + ("…" if len(compact) > 24 else "")
    return preview or f"文案 {position}"


def queue_public_snapshot() -> dict[str, Any]:
    main_job = snapshot_job("main")
    with QUEUE_LOCK:
        items: list[dict[str, Any]] = []
        completed_units = 0.0
        active_position = 0
        for item in QUEUE_ITEMS:
            status = str(item.get("status") or "pending")
            progress = float(item.get("progress") or 0)
            stage = str(item.get("stage") or "")
            if status == "running":
                progress = float(main_job.get("progress") or progress)
                stage = str(main_job.get("stage") or stage)
                active_position = int(item.get("position") or 0)
                completed_units += max(0, min(100, progress)) / 100
            elif status in {"done", "error", "cancelled"}:
                progress = 100
                completed_units += 1
            avatar_id = str(item.get("avatarId") or "")
            item_payload = item.get("payload") or {}
            generation_mode = normalize_elevenlabs_generation_mode(
                item_payload.get("elevenGenerationMode"), item_payload.get("elevenModelId")
            ) if item_payload.get("voiceMode") == "elevenlabs" else ""
            items.append({
                "id": item.get("id"),
                "position": item.get("position"),
                "title": item.get("title"),
                "characters": item.get("characters"),
                "avatarId": item.get("avatarId"),
                "avatarName": item.get("avatarName"),
                "voiceName": item.get("voiceName"),
                "voiceAccountName": item.get("voiceAccountName"),
                "elevenGenerationMode": generation_mode,
                "elevenGenerationModeName": (
                    elevenlabs_generation_mode_name(generation_mode) if generation_mode else ""
                ),
                "avatarPosterUrl": (
                    f"/api/avatar-media?id={urllib.parse.quote(avatar_id)}&kind=poster"
                    if avatar_id else None
                ),
                "status": status,
                "progress": round(progress, 1),
                "stage": stage,
                "result": item.get("result"),
                "cover": item.get("cover"),
                "error": item.get("error"),
                "createdAt": item.get("createdAt"),
                "startedAt": item.get("startedAt"),
                "finishedAt": item.get("finishedAt"),
                "quality": item_payload.get("quality"),
                "resolution": item_payload.get("resolution"),
                "brollEnabled": bool(item_payload.get("brollEnabled")),
                "musicId": item_payload.get("musicId"),
            })
        total = len(items)
        busy = any(item["status"] in {"pending", "running"} for item in items)
        running = any(item["status"] == "running" for item in items)
        pending = sum(1 for item in items if item["status"] == "pending")
        paused_items = sum(1 for item in items if item["status"] == "paused")
        completed = sum(1 for item in items if item["status"] == "done")
        failed = sum(1 for item in items if item["status"] == "error")
        overall = (completed_units / total * 100) if total else 0
        return {
            "ok": True,
            "status": (
                "running" if running else
                "paused" if busy and QUEUE_PAUSED else
                "running" if busy else
                "paused" if paused_items else
                "done" if total else "idle"
            ),
            "paused": QUEUE_PAUSED,
            "total": total,
            "pending": pending,
            "pausedItems": paused_items,
            "completed": completed,
            "failed": failed,
            "activePosition": active_position,
            "overallProgress": round(overall, 1),
            "items": items,
        }


def set_queue_awake(active: bool) -> None:
    try:
        flags = 0x80000000 | (0x00000001 if active else 0)
        ctypes.windll.kernel32.SetThreadExecutionState(flags)
    except Exception:
        pass


def module_environment(module_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    venv = module_root / "venv"
    prepend = [
        FFMPEG_DIR,
        venv / "Library" / "bin",
        venv / "DLLs",
        venv,
        venv / "Scripts",
        venv / "Lib" / "site-packages" / "torch" / "lib",
        venv / "Lib" / "site-packages" / "onnxruntime" / "capi",
    ]
    existing = env.get("PATH", "")
    env["PATH"] = os.pathsep.join([str(path) for path in prepend if path.exists()] + [existing])
    env["CONDA_PREFIX"] = str(venv)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    if module_root.name.lower() in {"humanmodule", "hdmodule"}:
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(
            [str(APP_DIR), str(module_root)] + ([existing_pythonpath] if existing_pythonpath else [])
        )
        env["BATCH_SIZE"] = str(MODEL_BATCH_SIZE)
        env["PARALLEL_FACE_DETECT"] = "1"
        env["PARALLEL_THREADS"] = "4"
        # The bundled cache is process-local and does not persist useful child data.
        env["LOCAL_DH_FACE_CACHE"] = "0"
        env["LOCAL_DH_FACE_CACHE_DIR"] = str((FACE_CACHE_DIR / module_root.name).resolve())
    return env


def format_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}小时{minutes}分"
    if minutes:
        return f"{minutes}分{seconds}秒"
    return f"{seconds}秒"


def cleanup_stale_model_processes(kind: str | None = None) -> int:
    """Remove orphaned digital-human runtimes left behind by packaged modules."""
    if psutil is None:
        return 0
    current_pid = os.getpid()
    targets = []
    markers = (
        "\\python-modules\\humanmodule\\venv\\python.exe",
        "\\python-modules\\hdmodule\\venv\\python.exe",
    )
    for process in psutil.process_iter(["pid", "exe"]):
        try:
            if process.pid == current_pid:
                continue
            executable = str(process.info.get("exe") or "").replace("/", "\\").lower()
            if any(marker in executable for marker in markers):
                targets.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    for process in targets:
        try:
            process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    _, alive = psutil.wait_procs(targets, timeout=5)
    for process in alive:
        try:
            process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if kind and targets:
        append_job_log(kind, f"已自动清理 {len(targets)} 个遗留数字人进程。")
    return len(targets)


def cleanup_stale_voice_processes(kind: str | None = None) -> int:
    """Remove voice API processes not owned by the current server instance."""
    if psutil is None:
        return 0
    active_pid = VOICE_PROCESS.pid if VOICE_PROCESS is not None and VOICE_PROCESS.poll() is None else None
    targets = []
    for process in psutil.process_iter(["pid", "exe", "cmdline"]):
        try:
            if process.pid == active_pid:
                continue
            executable = str(process.info.get("exe") or "").replace("/", "\\").lower()
            command = " ".join(process.info.get("cmdline") or []).replace("/", "\\").lower()
            is_legacy = "\\voicev2module\\venv\\python.exe" in executable and "\\voicev2module\\api.py" in command
            is_voxcpm = "\\voxcpm\\venv311\\scripts\\python.exe" in executable and "voxcpm_service.py" in command
            if is_legacy or is_voxcpm:
                targets.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    for process in targets:
        try:
            process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    _, alive = psutil.wait_procs(targets, timeout=8)
    for process in alive:
        try:
            process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if kind and targets:
        append_job_log(kind, f"已自动清理 {len(targets)} 个遗留声音进程。")
    return len(targets)


def _voice_process_match(executable: str, command: str) -> bool:
    return (
        "voxcpm_service.py" in command
        or ("\\voicev2module\\venv\\python.exe" in executable
            and "\\voicev2module\\api.py" in command)
    )


def cleanup_orphan_voice_processes() -> int:
    """Kill voice services left behind by a dead server instance (显存/内存双重占用).

    判定规则：沿父进程链向上走，穿过声音服务自己的多进程子进程后——
    链条断了（父进程已死，即上一个服务器实例的遗留）才是孤儿，按进程树清理；
    链条尽头是本程序 server.py（当前实例自己拉的，含 VOICE_PROCESS 子树）
    或任何其他活着的外部程序（轻语等）都不动。
    """
    if psutil is None:
        return 0
    voice_pids: set[int] = set()
    for process in psutil.process_iter(["pid", "exe", "cmdline"]):
        try:
            command = " ".join(process.info.get("cmdline") or []).replace("/", "\\").lower()
            executable = str(process.info.get("exe") or "").replace("/", "\\").lower()
            if _voice_process_match(executable, command):
                voice_pids.add(process.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    owned_pids: set[int] = set()
    if VOICE_PROCESS is not None and VOICE_PROCESS.poll() is None:
        try:
            owner = psutil.Process(VOICE_PROCESS.pid)
            owned_pids.add(owner.pid)
            owned_pids.update(child.pid for child in owner.children(recursive=True))
        except psutil.Error:
            owned_pids.add(VOICE_PROCESS.pid)
    orphan_roots = []
    for pid in sorted(voice_pids - owned_pids):
        if pid == os.getpid():
            continue
        try:
            process = psutil.Process(pid)
            orphan = True
            parent = process.parent()
            while parent is not None:
                if parent.pid in voice_pids:
                    parent = parent.parent()  # 穿过声音服务自己的子进程
                    continue
                # 第一个活着的非声音服务祖先：不管是谁拉起的都不动
                orphan = False
                break
            if orphan:
                orphan_roots.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    for process in orphan_roots:
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            try:
                process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return len(orphan_roots)


def gpu_free_memory_mb() -> int | None:
    command = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "nvidia-smi.exe"
    if not command.exists():
        return None
    try:
        result = subprocess.run(
            [str(command), "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        first = result.stdout.strip().splitlines()[0]
        return int(first.strip())
    except Exception:
        return None


def wait_for_gpu_memory(kind: str, minimum_mb: int = 0, timeout: int = 30) -> None:
    if not minimum_mb:
        # 动态读取：安装向导把 gpuMinFreeMB 写进 local-config.json 后无需重启即可生效
        minimum_mb = int(config_text("gpuMinFreeMB", "LOCAL_DH_GPU_MIN_FREE_MB") or GPU_MIN_FREE_MB)
    started = time.time()
    while True:
        raise_if_main_cancelled()
        free_mb = gpu_free_memory_mb()
        if free_mb is None or free_mb >= minimum_mb:
            return
        elapsed = int(time.time() - started)
        if elapsed >= timeout:
            raise RuntimeError(
                f"显卡可用显存只有 {free_mb}MB，至少需要约 {minimum_mb}MB。"
                "请关闭其他占用显卡的软件后重试。"
            )
        update_job(kind, stage=f"正在等待显卡释放（可用 {free_mb}MB）")
        time.sleep(2)


def http_json(url: str, data: dict[str, Any] | None = None, timeout: int = 30,
              headers: dict[str, str] | None = None) -> dict[str, Any]:
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
    request_headers = {"Accept": "application/json"}
    if body is not None:
        request_headers["Content-Type"] = "application/json; charset=utf-8"
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, data=body, headers=request_headers,
                                     method="POST" if body is not None else "GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def voice_health(engine: str = "v2") -> dict[str, Any] | None:
    port = VOICE_ENGINES.get(engine, VOICE_ENGINES["v2"])
    try:
        return http_json(f"http://127.0.0.1:{port}/health", timeout=2)
    except Exception:
        return None


def start_local_voice(kind: str, engine: str = "v2") -> None:
    global VOICE_PROCESS, VOICE_LOG_HANDLE, VOICE_ENGINE
    engine = engine if engine in VOICE_ENGINES else "v2"
    with VOICE_LOCK:
        if (
            VOICE_PROCESS is not None
            and VOICE_PROCESS.poll() is None
            and VOICE_ENGINE != engine
        ):
            stop_local_voice()

        health = voice_health(engine)
        if health and health.get("model_loaded"):
            if VOICE_PROCESS is None:
                if engine == "voxcpm":
                    raise RuntimeError("检测到其他程序正在占用 VoxCPM 声音服务，请先关闭对应程序后重试。")
                raise RuntimeError("检测到轻语或其他程序正在占用本地声音模型，请先在轻语中停止本地声音服务后重试。")
            return

        if VOICE_PROCESS is not None and VOICE_PROCESS.poll() is not None:
            VOICE_PROCESS = None

        if VOICE_PROCESS is None:
            if engine == "voxcpm":
                python_exe = VOXCPM_PYTHON
                api_script = VOXCPM_SERVICE
                work_dir = VOXCPM_ROOT
                log_name = "voice-voxcpm.log"
                missing_message = f"没有找到 VoxCPM 声音引擎，请确认已部署到 {VOXCPM_ROOT}。"
            else:
                work_dir = MODULES_ROOT / "voiceV2Module"
                python_exe = work_dir / "venv" / "python.exe"
                api_script = work_dir / "api.py"
                log_name = "voice-service.log"
                missing_message = (
                    "没有找到本地声音模块（此安装包未包含本地语音引擎，"
                    "请使用 ElevenLabs 云端声音或“自己录音”模式）。"
                )
            if not python_exe.exists() or not api_script.exists():
                raise RuntimeError(missing_message)
            log_path = LOG_DIR / log_name
            VOICE_LOG_HANDLE = log_path.open("a", encoding="utf-8", errors="replace")
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            if engine == "voxcpm":
                env = os.environ.copy()
                env["PYTHONUTF8"] = "1"
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUNBUFFERED"] = "1"
                env["VOXCPM_MODEL_DIR"] = str(VOXCPM_MODEL_DIR)
                env["VOXCPM_PORT"] = str(VOICE_ENGINES["voxcpm"])
                env["LOCAL_DH_FFMPEG_EXE"] = str(FFMPEG_EXE)
            else:
                env = module_environment(work_dir)
            VOICE_PROCESS = subprocess.Popen(
                [str(python_exe), str(api_script)],
                cwd=str(work_dir),
                env=env,
                stdout=VOICE_LOG_HANDLE,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags,
            )
            VOICE_ENGINE = engine

    started = time.time()
    stage_label = (
        "正在启动 VoxCPM 声音引擎（首次较慢）" if engine == "voxcpm"
        else "正在启动本地声音引擎（首次较慢）"
    )
    while time.time() - started < 360:
        process = VOICE_PROCESS
        if process is not None and process.poll() is not None:
            if engine == "voxcpm":
                raise RuntimeError("VoxCPM 声音引擎启动失败，请查看程序日志。")
            raise RuntimeError("本地声音模型启动失败，请查看程序日志。")
        health = voice_health(engine)
        if health and health.get("model_loaded"):
            return
        elapsed = time.time() - started
        if kind == "main":
            update_job(kind, progress=min(24, 7 + int(elapsed / 12)), stage=stage_label)
        elif kind in {"preview", "clone"}:
            update_job(kind, progress=min(50, 10 + int(elapsed / 7)), stage=stage_label)
        time.sleep(2)
    health = voice_health(engine)
    detail = str((health or {}).get("error") or "").strip()
    if detail:
        raise RuntimeError(f"声音模型加载超时。引擎报错：{detail[:200]}")
    raise RuntimeError("声音模型加载超时。")


def stop_local_voice() -> None:
    global VOICE_PROCESS, VOICE_LOG_HANDLE, VOICE_ENGINE
    with VOICE_LOCK:
        process = VOICE_PROCESS
        VOICE_PROCESS = None
        VOICE_ENGINE = None
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        if VOICE_LOG_HANDLE is not None:
            try:
                VOICE_LOG_HANDLE.close()
            except Exception:
                pass
            VOICE_LOG_HANDLE = None


def schedule_voice_stop(stamp: float, delay: float = 300.0) -> None:
    """闲置自动释放：delay 秒内没有任何生成用过声音服务，就把它停掉。

    任务进行中（主任务持锁 / 克隆进行中）不释放，稍后重新检查；
    期间若有生成用过服务（VOICE_LAST_USED 前进），定时器自动失效。
    """
    def stop_if_idle() -> None:
        if RUN_LOCK.locked() or snapshot_job("clone")["status"] == "running":
            schedule_voice_stop(stamp, 60.0)
            return
        if VOICE_LAST_USED <= stamp:
            stop_local_voice()
            cleanup_orphan_voice_processes()

    timer = threading.Timer(delay, stop_if_idle)
    timer.daemon = True
    timer.start()


def warm_local_voice() -> None:
    records = load_voice_records()
    if RUN_LOCK.locked() or not records:
        return
    if not VOICE_WARMUP_LOCK.acquire(blocking=False):
        return
    try:
        ready_local = next(
            (item for item in records
             if item.get("provider") == "local" and item.get("status") == "ready"),
            None,
        )
        engine = str((ready_local or {}).get("engine") or "v2")
        start_local_voice("warmup", engine)
        # 预热只为下次生成提速：5 分钟内没人用就自动释放显存（2026-08-16 起）
        schedule_voice_stop(VOICE_LAST_USED)
    except Exception:
        pass
    finally:
        VOICE_WARMUP_LOCK.release()


def schedule_voice_warmup(delay: float = 2.0) -> None:
    timer = threading.Timer(delay, warm_local_voice)
    timer.daemon = True
    timer.start()


def generate_local_voice(kind: str, text: str, prompt_audio: Path, prompt_text: str,
                         output_path: Path, speed: float, *, job_stage: str | None = None,
                         job_progress: int | None = None, engine: str = "v2",
                         emotion_weight: float = 1.0, emotion_text: str = "",
                         cfg_value: float = 2.0, inference_timesteps: int = 10) -> Path:
    global VOICE_LAST_USED
    engine = engine if engine in VOICE_ENGINES else "v2"
    start_local_voice(kind, engine)
    if job_stage is not None:
        update_job(kind, stage=job_stage, progress=job_progress)
    elif kind == "clone":
        update_job(kind, stage="正在克隆声音并生成试听", progress=55)
    else:
        update_job(kind, stage="正在用所选声音合成文案", progress=54 if kind == "preview" else 27)
    payload = {
        "text": text,
        "prompt_text": prompt_text,
        "prompt_audio_path": str(prompt_audio),
        "output_path": str(output_path),
        "speed": speed,
        "emotion_weight": emotion_weight,
        "emotion_text": emotion_text,
        "cfg_value": cfg_value,
        "inference_timesteps": inference_timesteps,
    }
    heartbeat_stop = threading.Event()
    started = time.time()
    base_stage = job_stage or ("正在克隆声音并生成试听" if kind == "clone" else "正在用所选声音合成文案")

    def report_elapsed() -> None:
        while not heartbeat_stop.wait(5):
            elapsed = time.time() - started
            update_job(
                kind,
                stage=f"{base_stage} · 已用时 {format_duration(elapsed)}",
                elapsedSeconds=int(elapsed),
            )

    heartbeat = threading.Thread(target=report_elapsed, daemon=True)
    heartbeat.start()
    try:
        result = http_json(f"http://127.0.0.1:{VOICE_ENGINES[engine]}/generate", data=payload, timeout=1200)
    finally:
        heartbeat_stop.set()
        heartbeat.join(timeout=0.2)
    if result.get("code") != 200:
        raise RuntimeError(result.get("msg") or "本地声音生成失败。")
    generated = Path((result.get("data") or {}).get("output_path") or output_path)
    if not generated.exists():
        raise RuntimeError("声音接口已返回完成，但没有找到生成的音频。")
    VOICE_LAST_USED = time.time()
    return generated


def normalize_elevenlabs_generation_mode(value: Any, model_id: Any = "") -> str:
    requested = str(value or "").strip()
    if requested in ELEVENLABS_GENERATION_MODE_MAP:
        return requested
    model = str(model_id or "").strip()
    if model == "eleven_v3":
        return "v3"
    if model == "eleven_turbo_v2":
        return "turbo_v2"
    return "multilingual_v2"


def elevenlabs_model_for_mode(mode: Any, fallback: Any = "") -> str:
    normalized = normalize_elevenlabs_generation_mode(mode, fallback)
    return str(ELEVENLABS_GENERATION_MODE_MAP[normalized]["modelId"])


def elevenlabs_generation_mode_name(mode: Any) -> str:
    normalized = normalize_elevenlabs_generation_mode(mode)
    return str(ELEVENLABS_GENERATION_MODE_MAP[normalized]["name"])


def generate_elevenlabs_voice(text: str, api_key: str, voice_id: str,
                              output_path: Path, speed: float,
                              model_id: str = "eleven_multilingual_v2",
                              output_format: str = "mp3_44100_128",
                              settings: dict[str, Any] | None = None) -> Path:
    encoded_voice = urllib.parse.quote(voice_id.strip(), safe="")
    output_format = (
        output_format if output_format in ELEVENLABS_OUTPUT_FORMAT_IDS else "mp3_44100_128"
    )
    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{encoded_voice}"
        f"?output_format={urllib.parse.quote(output_format, safe='')}"
    )
    voice_preset = normalize_elevenlabs_settings(settings)
    voice_settings = {
        "stability": voice_preset["stability"],
        "similarity_boost": voice_preset["similarityBoost"],
        "style": voice_preset["style"],
        "use_speaker_boost": voice_preset["speakerBoost"],
        "speed": max(0.7, min(1.2, speed)),
    }
    if model_id == "eleven_v3":
        voice_settings.pop("style", None)
        voice_settings.pop("use_speaker_boost", None)
    payload = {
        "text": text,
        "model_id": model_id or "eleven_multilingual_v2",
        "voice_settings": voice_settings,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key.strip(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            output_path.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            detail = str(parsed.get("detail") or parsed)
        except Exception:
            pass
        raise RuntimeError(f"ElevenLabs 调用失败：{detail[:300]}") from exc
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("ElevenLabs 没有返回有效音频。")
    return output_path


def encode_elevenlabs_multipart(
    audio_path: Path, fields: dict[str, str]
) -> tuple[bytes, str]:
    boundary = f"----LocalDigitalHuman{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode("ascii"),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
            str(value).encode("utf-8"),
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


def convert_elevenlabs_voice(
    api_key: str,
    voice_id: str,
    source_audio: Path,
    output_path: Path,
    output_format: str = "mp3_44100_128",
    settings: dict[str, Any] | None = None,
) -> Path:
    if not source_audio.is_file() or source_audio.stat().st_size == 0:
        raise ValueError("Voice Changer 缺少有效的来源音频。")
    output_format = (
        output_format if output_format in ELEVENLABS_OUTPUT_FORMAT_IDS else "mp3_44100_128"
    )
    preset = normalize_elevenlabs_settings(settings)
    voice_settings = {
        "stability": max(0.65, float(preset["stability"])),
        "similarity_boost": max(0.90, float(preset["similarityBoost"])),
        "style": 0.0,
        "use_speaker_boost": True,
    }
    body, boundary = encode_elevenlabs_multipart(source_audio, {
        "model_id": "eleven_multilingual_sts_v2",
        "voice_settings": json.dumps(voice_settings, ensure_ascii=False),
        "remove_background_noise": "false",
    })
    encoded_voice = urllib.parse.quote(voice_id.strip(), safe="")
    url = (
        f"https://api.elevenlabs.io/v1/speech-to-speech/{encoded_voice}"
        f"?output_format={urllib.parse.quote(output_format, safe='')}"
    )
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "xi-api-key": api_key.strip(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            output_path.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            detail = str(parsed.get("detail") or parsed)
        except Exception:
            pass
        raise RuntimeError(f"ElevenLabs 音色转换失败：{detail[:300]}") from exc
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("ElevenLabs 音色转换没有返回有效音频。")
    return output_path


def semantic_text_tokens(text: str) -> list[str]:
    """Tokenize text without separating normal Chinese words across chunks."""
    tokens: list[str] = []
    for block in re.findall(
        r"[\u3400-\u9fff]+|[A-Za-z0-9]+(?:[._'’\-][A-Za-z0-9]+)*|\s+|.",
        text,
        flags=re.S,
    ):
        if re.fullmatch(r"[\u3400-\u9fff]+", block):
            if jieba is not None:
                tokens.extend(token for token in jieba.lcut(block, cut_all=False) if token)
            else:
                # Do not fall back to single characters. Two-character groups
                # preserve the majority of common Chinese words when jieba is
                # unavailable in a portable installation.
                tokens.extend(block[index:index + 2] for index in range(0, len(block), 2))
        else:
            tokens.append(block)
    return tokens


def split_at_semantic_boundaries(text: str, max_chars: int) -> list[str]:
    """Split an overlong clause at word boundaries instead of raw characters."""
    chunks: list[str] = []
    current = ""
    for token in semantic_text_tokens(text):
        candidate = current + token
        if current and len(candidate.strip()) > max_chars and token.strip():
            chunks.append(current.strip())
            current = token.lstrip()
        else:
            current = candidate
    if current.strip():
        chunks.append(current.strip())
    return chunks


def split_script_text(text: str, max_chars: int) -> list[str]:
    """Split narration on natural punctuation while keeping every spoken character."""
    normalized = re.sub(r"[ \t]+", " ", text.replace("\r\n", "\n").replace("\r", "\n")).strip()
    if not normalized:
        return []

    sentence_units = [
        match.group(0).strip()
        for match in re.finditer(r".*?(?:[。！？!?；;…]+|\n+|$)", normalized, flags=re.S)
        if match.group(0).strip()
    ]
    small_units: list[str] = []
    for unit in sentence_units:
        if len(unit) <= max_chars:
            small_units.append(unit)
            continue
        clauses = [
            match.group(0).strip()
            for match in re.finditer(r".*?(?:[，,、：:]+|$)", unit, flags=re.S)
            if match.group(0).strip()
        ]
        for clause in clauses or [unit]:
            if len(clause) <= max_chars:
                small_units.append(clause)
            else:
                small_units.extend(split_at_semantic_boundaries(clause, max_chars))

    chunks: list[str] = []
    current = ""
    for unit in small_units:
        separator = " " if current and current[-1].isalnum() and unit[0].isalnum() else ""
        candidate = current + separator + unit
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = unit
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def merge_audio_segments(segment_paths: list[Path], output_path: Path, work_dir: Path) -> Path:
    if not segment_paths:
        raise RuntimeError("没有生成可合并的声音片段。")
    if not FFMPEG_EXE.exists():
        raise RuntimeError("没有找到声音合并组件。")

    concat_file = work_dir / "audio_segments.txt"
    concat_file.write_text(
        "".join(f"file '{str(path.resolve()).replace(chr(92), '/')}'\n" for path in segment_paths),
        encoding="utf-8",
    )
    output_path.unlink(missing_ok=True)
    completed = subprocess.run(
        [
            str(FFMPEG_EXE), "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-vn", "-ac", "1", "-ar", "22050", "-c:a", "pcm_s16le", str(output_path),
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=3600, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not output_path.is_file() or output_path.stat().st_size <= 44:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"分段声音合并失败。{completed.stderr[-500:]}")
    return output_path


def media_duration(media_path: Path) -> float:
    if not FFPROBE_EXE.exists() or not media_path.is_file():
        return 0.0
    completed = subprocess.run(
        [str(FFPROBE_EXE), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(media_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        return 0.0
    try:
        return max(0.0, float((completed.stdout or "0").strip()))
    except ValueError:
        return 0.0


def prune_voice_checkpoints() -> None:
    cutoff = time.time() - CHECKPOINT_MAX_AGE_SECONDS
    for directory in VOICE_CHECKPOINT_DIR.iterdir():
        try:
            if directory.is_dir() and directory.stat().st_mtime < cutoff:
                shutil.rmtree(directory, ignore_errors=True)
        except OSError:
            continue


def voice_checkpoint_dir(data: dict[str, Any], segments: list[str]) -> Path:
    identity: dict[str, Any] = {
        "version": 2,
        "mode": data["voiceMode"],
        "segments": segments,
        "speed": data["speed"],
    }
    if data["voiceMode"] == "local":
        sample: Path = data["promptAudio"]
        sample_stat = sample.stat()
        identity.update({
            "localVoiceId": data.get("localVoiceId") or "",
            "sample": str(sample.resolve()),
            "sampleSize": sample_stat.st_size,
            "sampleModified": sample_stat.st_mtime_ns,
            "promptText": data["promptText"],
            "emotionWeight": data.get("emotionWeight", 1.0),
            "emotionText": data.get("emotionText") or "",
            "cfgValue": data.get("cfgValue", 2.0),
            "inferenceTimesteps": data.get("inferenceTimesteps", 10),
        })
    elif data["voiceMode"] == "upload":
        audio: Path = data["customAudio"]
        audio_stat = audio.stat()
        identity.update({
            "customAudio": str(audio.resolve()),
            "audioSize": audio_stat.st_size,
            "audioModified": audio_stat.st_mtime_ns,
        })
    else:
        identity.update({
            "voiceId": data["voiceId"],
            "accountId": data.get("elevenAccountId") or "",
            "generationMode": data.get("elevenGenerationMode") or "multilingual_v2",
            "modelId": data.get("elevenModelId") or "eleven_multilingual_v2",
            "outputFormat": data.get("elevenOutputFormat") or "mp3_44100_128",
            "settings": data.get("elevenSettings") or {},
        })
    fingerprint = hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return VOICE_CHECKPOINT_DIR / fingerprint


def valid_audio_part(path: Path, local_mode: bool) -> bool:
    minimum = 44 if local_mode else 128
    return path.is_file() and path.stat().st_size > minimum


def prepare_uploaded_script_audio(data: dict[str, Any], output_path: Path) -> Path:
    """用户自己录音驱动数字人：跳过语音合成，整段录音直接与整篇文案逐字对齐。

    录音只转码一次并缓存进语音断点目录（按录音文件指纹区分），重复提交同一篇
    文案 + 同一段录音时直接复用。对齐走 align_subtitle_cues 的长音频两遍分块，
    对真人朗读同样成立；朗读与文案有出入时强制对齐仍按给定文案贴时间轴。
    """
    source: Path = data["customAudio"]
    if not source.is_file():
        raise ValueError("录音文件不存在或已被清理，请重新上传。")
    segments = [data["text"]]
    prune_voice_checkpoints()
    work_dir = voice_checkpoint_dir(data, segments)
    work_dir.mkdir(parents=True, exist_ok=True)
    part_path = work_dir / "part_00001.wav"
    if not valid_audio_part(part_path, False):
        raise_if_main_cancelled()
        update_job("main", stage="正在处理录音", progress=18)
        temporary = work_dir / "part_00001.part.wav"
        temporary.unlink(missing_ok=True)
        completed = subprocess.run(
            [str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(source),
             "-vn", "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le", str(temporary)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=1800, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode != 0 or not temporary.is_file() or temporary.stat().st_size <= 44:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f"录音转码失败：{(completed.stderr or '')[-200:]}")
        temporary.replace(part_path)
    duration = media_duration(part_path)
    if duration <= 0.5:
        raise ValueError("录音太短或无法读取，请重新录制。")
    update_job(
        "main", segmentsTotal=1, segmentsDone=1,
        stage=f"录音已就绪（{format_duration(duration)}）", progress=30,
    )
    append_job_log("main", "使用上传的本人录音，已跳过语音合成。")
    generated_parts = [part_path]
    if data.get("subtitleEnabled"):
        try:
            data["subtitleSegments"] = [{"text": data["text"], "duration": duration}]
        except Exception as exc:
            data["subtitleSegments"] = []
            append_job_log("main", f"读取字幕分段时长失败，将自动使用整段时间：{exc}")
    if data.get("subtitleEnabled") or data.get("brollEnabled"):
        update_job("main", stage="正在对齐录音与文案", progress=34)
        try:
            data["subtitleCues"] = align_subtitle_cues(segments, generated_parts)
        except TaskCancelled:
            raise
        except Exception as exc:
            data["subtitleCues"] = []
            append_job_log("main", f"字幕逐字对齐未完成，改用估算时间：{exc}")
    update_job("main", stage="正在整理录音", progress=44, estimatedSeconds=None)
    return merge_audio_segments(generated_parts, output_path, work_dir)


def generate_segmented_script_audio(data: dict[str, Any], output_path: Path) -> Path:
    if data["voiceMode"] == "upload":
        return prepare_uploaded_script_audio(data, output_path)
    local_mode = data["voiceMode"] == "local"
    max_chars = LOCAL_VOICE_SEGMENT_CHARS if local_mode else ELEVENLABS_SEGMENT_CHARS
    segments = split_script_text(data["text"], max_chars)
    if not segments:
        raise ValueError("请先输入文案。")

    total = len(segments)
    prune_voice_checkpoints()
    work_dir = voice_checkpoint_dir(data, segments)
    work_dir.mkdir(parents=True, exist_ok=True)
    generated_parts: list[Path] = []
    update_job(
        "main", segmentsTotal=total, segmentsDone=0,
        stage=f"已自动拆分为 {total} 段", progress=25 if local_mode else 16,
    )
    append_job_log("main", f"长文案已自动拆分为 {total} 段。")

    manifest_path = work_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps({"segments": segments, "updatedAt": time.time()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    synthesis_started = time.time()
    fresh_durations: list[float] = []
    for index, segment in enumerate(segments, start=1):
        raise_if_main_cancelled()
        base_progress = 25 if local_mode else 16
        end_progress = 43
        progress = base_progress + int((index - 1) / total * (end_progress - base_progress))
        stage = f"正在合成第 {index}/{total} 段声音"
        suffix = ".wav" if local_mode else ".mp3"
        part_path = work_dir / f"part_{index:05d}{suffix}"

        if valid_audio_part(part_path, local_mode):
            generated_parts.append(part_path)
            update_job(
                "main", segmentsDone=index, progress=progress,
                stage=f"已恢复第 {index}/{total} 段声音",
            )
            append_job_log("main", f"第 {index}/{total} 段已从上次进度恢复。")
            continue

        part_started = time.time()

        if local_mode:
            last_error: Exception | None = None
            for attempt in range(1, LOCAL_VOICE_SEGMENT_RETRIES + 1):
                try:
                    part_path.unlink(missing_ok=True)
                    generate_local_voice(
                        "main", segment, data["promptAudio"], data["promptText"],
                        part_path, data["speed"], job_stage=stage, job_progress=progress,
                        engine=data.get("voiceEngine") or "v2",
                        emotion_weight=data.get("emotionWeight", 1.0),
                        emotion_text=data.get("emotionText") or "",
                        cfg_value=data.get("cfgValue", 2.0),
                        inference_timesteps=data.get("inferenceTimesteps", 10),
                    )
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    append_job_log(
                        "main", f"第 {index}/{total} 段第 {attempt} 次生成失败：{exc}",
                    )
                    stop_local_voice()
                    if attempt < LOCAL_VOICE_SEGMENT_RETRIES:
                        update_job(
                            "main", stage=f"第 {index}/{total} 段中断，正在自动重试",
                            progress=progress,
                        )
                        time.sleep(2)
            if last_error is not None:
                raise RuntimeError(
                    f"第 {index}/{total} 段声音连续重试 {LOCAL_VOICE_SEGMENT_RETRIES} 次仍失败：{last_error}"
                ) from last_error
        else:
            generation_mode = normalize_elevenlabs_generation_mode(
                data.get("elevenGenerationMode"), data.get("elevenModelId")
            )
            if generation_mode == "v3_voice_match":
                v3_source = work_dir / f"part_{index:05d}_v3_source.mp3"
                source_progress = progress
                convert_progress = min(
                    42,
                    progress + max(1, int((end_progress - base_progress) / max(total * 2, 1))),
                )
                if not valid_audio_part(v3_source, False):
                    update_job(
                        "main",
                        stage=f"第 {index}/{total} 段：V3 正在生成情感声音",
                        progress=source_progress,
                    )
                    source_settings = dict(data["elevenSettings"])
                    source_settings["stability"] = 0.50
                    source_settings["similarityBoost"] = max(
                        0.85, float(source_settings.get("similarityBoost") or 0.75)
                    )
                    generate_elevenlabs_voice(
                        segment, data["apiKey"], data["voiceId"], v3_source, data["speed"],
                        "eleven_v3", data["elevenOutputFormat"], source_settings,
                    )
                    record_elevenlabs_usage(
                        data.get("elevenAccountId") or "", len(segment)
                    )
                else:
                    append_job_log(
                        "main", f"第 {index}/{total} 段 V3 情感声音已从上次进度恢复。"
                    )
                update_job(
                    "main",
                    stage=f"第 {index}/{total} 段：正在转换回本人音色",
                    progress=convert_progress,
                )
                convert_elevenlabs_voice(
                    data["apiKey"], data["voiceId"], v3_source, part_path,
                    data["elevenOutputFormat"], data["elevenSettings"],
                )
                # STS 计费系数校准（2026-08-16）：按平台真实用量反推约 430 额度/分钟音频，
                # 原 1000/分钟明显高估；取 450 留少量余量，任务结束后还会自动同步平台真值修正
                conversion_units = max(1, round(media_duration(v3_source) * 450 / 60))
                record_elevenlabs_usage(
                    data.get("elevenAccountId") or "", conversion_units
                )
            else:
                update_job("main", stage=stage, progress=progress)
                generate_elevenlabs_voice(
                    segment, data["apiKey"], data["voiceId"], part_path, data["speed"],
                    data["elevenModelId"], data["elevenOutputFormat"], data["elevenSettings"],
                )
                record_elevenlabs_usage(
                    data.get("elevenAccountId") or "", len(segment)
                )

        generated_parts.append(part_path)
        fresh_durations.append(time.time() - part_started)
        remaining = (sum(fresh_durations) / len(fresh_durations)) * (total - index)
        remaining_label = "" if remaining <= 0 else f" · 声音约剩 {format_duration(remaining)}"
        update_job(
            "main", segmentsDone=index,
            elapsedSeconds=int(time.time() - synthesis_started),
            estimatedSeconds=int(remaining),
            stage=f"第 {index}/{total} 段声音已完成{remaining_label}",
        )
        manifest_path.write_text(
            json.dumps(
                {"segments": segments, "completed": index, "updatedAt": time.time()},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )

    if data.get("subtitleEnabled"):
        try:
            data["subtitleSegments"] = [
                {"text": segment, "duration": media_duration(part)}
                for segment, part in zip(segments, generated_parts)
            ]
        except Exception as exc:
            data["subtitleSegments"] = []
            append_job_log("main", f"读取字幕分段时长失败，将自动使用整段时间：{exc}")
    if data.get("subtitleEnabled") or data.get("brollEnabled"):
        try:
            data["subtitleCues"] = align_subtitle_cues(segments, generated_parts)
        except TaskCancelled:
            raise
        except Exception as exc:
            data["subtitleCues"] = []
            append_job_log("main", f"字幕逐字对齐未完成，改用估算时间：{exc}")
    update_job("main", stage=f"正在合并 {total} 段声音", progress=44, estimatedSeconds=None)
    return merge_audio_segments(generated_parts, output_path, work_dir)


def parse_progress(line: str) -> float | None:
    if re.search(r"\x1b\[[0-9;?]*[A-Za-z]", line):
        return None
    clean = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", line)
    tqdm_matches = re.findall(r"(?<!\d)(100|\d{1,2})(?:\.\d+)?%.*?(\d+)\s*/\s*(\d+)", clean)
    useful = []
    for percent, current, total in tqdm_matches:
        total_value = int(total)
        if total_value < 20:
            rate_match = re.search(r"([\d.]+)it/s", clean)
            is_outer = "s/it" in clean or (rate_match and float(rate_match.group(1)) <= 4.5)
            if not is_outer and float(percent) > 0:
                continue
        useful.append((float(percent), int(current), total_value))
    if useful:
        percent, current, total = max(useful, key=lambda item: item[2])
        return max(percent, current / max(total, 1) * 100)
    if "progress" in clean.lower() or "进度" in clean:
        percentages = re.findall(r"(?<!\d)(100|\d{1,2})(?:\.\d+)?\s*%", clean)
        if percentages:
            return float(percentages[-1])
    try:
        data_start = clean.find("{")
        if data_start >= 0:
            payload = json.loads(clean[data_start:])
            for key in ("progress", "percent", "percentage"):
                if key in payload:
                    value = float(payload[key])
                    return value * 100 if 0 <= value <= 1 else value
    except Exception:
        return None
    return None


def find_media_path(value: Any) -> Path | None:
    if isinstance(value, str):
        candidate = Path(value)
        if candidate.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv"} and candidate.exists():
            return candidate
    if isinstance(value, dict):
        preferred = ("output_path", "output_file", "video_path", "file_path", "path", "result", "data")
        for key in preferred:
            if key in value:
                found = find_media_path(value[key])
                if found:
                    return found
        for child in value.values():
            found = find_media_path(child)
            if found:
                return found
    if isinstance(value, (list, tuple)):
        for child in value:
            found = find_media_path(child)
            if found:
                return found
    return None


def kill_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        try:
            process.kill()
        except Exception:
            pass
    if process.poll() is None:
        try:
            process.kill()
        except Exception:
            pass


def newest_video(output_dir: Path, started: float) -> Path | None:
    candidates: list[Path] = []
    try:
        for suffix in ("*.mp4", "*.mov", "*.avi", "*.mkv"):
            candidates.extend(path for path in output_dir.rglob(suffix)
                              if path.is_file() and path.stat().st_mtime >= started - 10)
    except Exception:
        pass
    return max(candidates, key=lambda item: item.stat().st_mtime) if candidates else None


def video_info(video_path: Path) -> dict[str, Any]:
    if not FFPROBE_EXE.exists():
        raise RuntimeError("没有找到视频分辨率检测组件。")
    completed = subprocess.run(
        [str(FFPROBE_EXE), "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,codec_name,pix_fmt,avg_frame_rate:format=duration",
         "-of", "json", str(video_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        raise RuntimeError("无法读取生成视频的分辨率。")
    streams = json.loads(completed.stdout or "{}").get("streams") or []
    if not streams:
        raise RuntimeError("生成的视频没有有效画面。")
    payload = json.loads(completed.stdout or "{}")
    stream = streams[0]
    duration = float((payload.get("format") or {}).get("duration") or 0)
    fps_text = str(stream.get("avg_frame_rate") or "0/1")
    try:
        numerator, denominator = fps_text.split("/", 1)
        fps = float(numerator) / max(float(denominator), 1.0)
    except Exception:
        fps = 0.0
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "codec": str(stream.get("codec_name") or ""),
        "pixFmt": str(stream.get("pix_fmt") or ""),
        "fps": fps,
        "duration": duration,
    }


def video_dimensions(video_path: Path) -> tuple[int, int]:
    info = video_info(video_path)
    return int(info["width"]), int(info["height"])


def choose_avatar_start_offset(avatar_path: Path, duration: float, clip_duration: float) -> float:
    """Rotate long avatar footage through randomized three-second slots and remember recent starts."""
    max_start = max(0.0, duration - clip_duration)
    if max_start < 3.0:
        return 0.0
    slot_count = int(max_start // 3.0) + 1
    with AVATAR_LOCK:
        records = load_avatar_records()
        resolved = avatar_path.resolve()
        record = next(
            (
                item for item in records
                if (AVATAR_DIR / str(item.get("video") or "")).resolve() == resolved
            ),
            None,
        )
        recent_slots: list[int] = []
        if record is not None:
            for value in record.get("recentStartOffsets") or []:
                try:
                    recent_slots.append(round(float(value) / 3.0))
                except (TypeError, ValueError):
                    continue
        available = [slot for slot in range(slot_count) if slot not in recent_slots[-24:]]
        if not available:
            available = list(range(slot_count))
        selected_slot = random.SystemRandom().choice(available)
        offset = min(max_start, selected_slot * 3.0)
        if record is not None:
            recent = [float(value) for value in record.get("recentStartOffsets") or []]
            recent.append(round(offset, 3))
            record["recentStartOffsets"] = recent[-24:]
            record["lastStartOffset"] = round(offset, 3)
            record["usageCount"] = int(record.get("usageCount") or 0) + 1
            save_avatar_records(records)
        return round(offset, 3)


def prepare_avatar_for_model(kind: str, avatar_path: Path, quality: str) -> tuple[Path, tuple[int, int]]:
    """Create a short, 8-bit H.264 model template so packaged modules never load 4K videos into RAM.

    长边上限 1920（2026-08-15 从 1280 上调）：1280 放大到 4K 导出偏糊，
    1920 在 RTX 3080 10GB 上实测可承受，导出清晰度明显改善；再大内存风险陡增。
    """
    if not FFMPEG_EXE.exists():
        raise RuntimeError("没有找到数字人素材优化组件。")
    info = video_info(avatar_path)
    source_width, source_height = int(info["width"]), int(info["height"])
    if source_width < 2 or source_height < 2 or float(info["duration"]) <= 0:
        raise RuntimeError("数字人形象视频没有有效画面。")

    max_long_edge = 1920
    max_duration = 20.0
    start_offset = choose_avatar_start_offset(
        avatar_path, float(info["duration"]), min(max_duration, float(info["duration"]))
    )
    already_safe = (
        start_offset <= 0.001
        and
        max(source_width, source_height) <= max_long_edge
        and float(info["duration"]) <= max_duration
        and info["codec"] == "h264"
        and info["pixFmt"] in {"yuv420p", "yuvj420p"}
        and 24.5 <= float(info["fps"]) <= 25.5
    )
    if already_safe:
        return avatar_path, (source_width, source_height)

    stat = avatar_path.stat()
    profile = f"safe-v4-{quality}-{max_long_edge}-{max_duration}-{start_offset:.3f}-25-h264"
    fingerprint = hashlib.sha256(
        f"{avatar_path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{profile}".encode("utf-8")
    ).hexdigest()[:24]
    prepared = MODEL_INPUT_DIR / f"{fingerprint}.mp4"
    if prepared.is_file() and prepared.stat().st_size > 1024:
        return prepared, (source_width, source_height)

    scale = min(1.0, max_long_edge / max(source_width, source_height))
    target_width = max(2, int(round(source_width * scale / 2) * 2))
    target_height = max(2, int(round(source_height * scale / 2) * 2))
    temporary = prepared.with_name(f"{prepared.stem}.part.mp4")
    temporary.unlink(missing_ok=True)
    update_job(kind, stage="正在优化数字人素材", progress=48)
    completed = subprocess.run(
        [str(FFMPEG_EXE), "-loglevel", "error", "-y", "-ss", f"{start_offset:.3f}",
         "-i", str(avatar_path),
         "-map", "0:v:0", "-t", f"{max_duration:.3f}",
         "-vf", f"fps=25,scale={target_width}:{target_height}:flags=lanczos",
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=1800, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not temporary.is_file() or temporary.stat().st_size <= 1024:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"数字人素材优化失败。{completed.stderr[-500:]}")
    temporary.replace(prepared)
    append_job_log(
        kind,
        f"数字人本次从 {start_offset:.1f} 秒开始取景；"
        f"形象素材已优化：{source_width}x{source_height} / {info['duration']:.1f}秒 → "
        f"{target_width}x{target_height} / {min(float(info['duration']), max_duration):.1f}秒",
    )
    return prepared, (source_width, source_height)


def subtitle_visual_units(text: str) -> float:
    """Approximate rendered width after subtitle punctuation is removed."""
    units = 0.0
    for character in text:
        if re.match(r"[\u3400-\u9fff]", character):
            units += 1.0
        elif character.isalnum():
            units += 0.55
        elif character.isspace():
            units += 0.3
    return units


def balanced_subtitle_token_chunks(text: str, max_units: float) -> list[str]:
    """Balance an overlong clause across word-safe lines without orphan tails."""
    tokens: list[str] = []
    for token in semantic_text_tokens(text):
        if subtitle_visual_units(token) <= 0 and tokens:
            tokens[-1] += token
        elif token:
            tokens.append(token)
    if not tokens:
        return [text.strip()] if text.strip() else []

    total_units = sum(subtitle_visual_units(token) for token in tokens)
    chunk_count = max(1, int((total_units + max_units - 0.001) // max_units))
    chunks: list[str] = []
    start = 0
    remaining_units = total_units
    for chunk_index in range(chunk_count - 1):
        remaining_chunks = chunk_count - chunk_index
        target = remaining_units / remaining_chunks
        minimum = max(0.0, remaining_units - (remaining_chunks - 1) * max_units)
        running = 0.0
        candidates: list[tuple[float, int, float]] = []
        # Leave at least one semantic token for every remaining chunk.
        latest = len(tokens) - (remaining_chunks - 1)
        for index in range(start, latest):
            running += subtitle_visual_units(tokens[index])
            if minimum <= running <= max_units:
                end_word = re.sub(r"[^\w\u3400-\u9fff]", "", tokens[index])
                next_word = (
                    re.sub(r"[^\w\u3400-\u9fff]", "", tokens[index + 1])
                    if index + 1 < len(tokens) else ""
                )
                boundary_penalty = 0.0
                if end_word in {
                    "把", "被", "让", "将", "给", "向", "对", "和", "与", "及", "或",
                    "想", "要", "会", "能", "可", "应", "做", "说", "看", "听", "去", "来",
                }:
                    boundary_penalty += 5.0
                if next_word in {
                    "清楚", "明白", "完成", "做好", "做到", "出来", "起来", "下去", "下来",
                    "进去", "出去", "过来", "过去", "干净", "准确", "完整", "透彻", "懂", "透",
                }:
                    boundary_penalty += 6.0
                if next_word in {
                    "以后", "然后", "所以", "但是", "不过", "因此", "同时", "最后", "接着",
                    "才能", "才会", "就会", "就能", "再", "而且", "如果", "只有",
                }:
                    boundary_penalty -= 2.0
                candidates.append((abs(running - target) + boundary_penalty, index + 1, running))
            if running > max_units:
                break
        if not candidates:
            break
        _, end, used_units = min(candidates, key=lambda item: (item[0], -item[2]))
        chunks.append("".join(tokens[start:end]).strip())
        start = end
        remaining_units -= used_units
    tail = "".join(tokens[start:]).strip()
    if tail:
        chunks.append(tail)
    return chunks


def split_overlong_subtitle_sentence(sentence: str, max_units: float) -> list[str]:
    """Prefer clause boundaries, then word boundaries, for an overlong sentence."""
    clauses = [
        match.group(0).strip()
        for match in re.finditer(r".*?(?:[，,、：:；;]+|$)", sentence, flags=re.S)
        if match.group(0).strip()
    ] or [sentence]

    pieces: list[str] = []
    current = ""
    for clause in clauses:
        if subtitle_visual_units(clause) > max_units:
            if current:
                pieces.append(current.strip())
                current = ""
            pieces.extend(balanced_subtitle_token_chunks(clause, max_units))
            continue

        candidate = current + clause
        if current and subtitle_visual_units(candidate) > max_units:
            pieces.append(current.strip())
            current = clause
        else:
            current = candidate
    if current.strip():
        pieces.append(current.strip())
    return pieces


def subtitle_chunks(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", normalized))
    # Keep a complete sentence on screen whenever it fits the portrait safe
    # area. Only overlong sentences may be split, first at punctuation and then
    # at semantic word boundaries.
    # At the current portrait subtitle size and 12% left/right margins, twelve
    # full-width Chinese glyphs are the one-line platform-safe capacity.
    max_units = 12.0 if cjk_count >= max(1, len(normalized) // 4) else 34.0
    sentences = [
        match.group(0).strip()
        for match in re.finditer(r".*?(?:[。！？!?；;…]+|$)", normalized, flags=re.S)
        if match.group(0).strip()
    ]
    chunks: list[str] = []
    for sentence in sentences or [normalized]:
        if subtitle_visual_units(sentence) <= max_units:
            chunks.append(sentence)
        else:
            chunks.extend(split_overlong_subtitle_sentence(sentence, max_units))
    return [chunk for chunk in chunks if re.search(r"[\w\u3400-\u9fff]", chunk)]


def subtitle_weight(text: str) -> int:
    return max(1, len(re.sub(r"[\s，。！？!?；;、：:…,.]", "", text)))


def subtitle_timing_weight(text: str) -> float:
    pause_weight = 0.0
    pause_weight += len(re.findall(r"[，,、：:]", text)) * 0.7
    pause_weight += len(re.findall(r"[。！？!?；;…]", text)) * 1.8
    return subtitle_weight(text) + pause_weight


def subtitle_display_text(text: str) -> str:
    without_punctuation = re.sub(
        r"[，。！？!?；;、：:…,.‘’“”\"'（）()【】\[\]《》〈〉—–\-~～·•/\\]",
        "",
        text,
    )
    return re.sub(r"\s+", " ", without_punctuation).strip()


def format_title_lines(text: str) -> str:
    title = normalize_video_title(text)
    lines = split_cover_title_lines(title)
    return "\n".join(lines) if lines else title


def build_subtitle_cues(text: str, duration: float,
                        timed_segments: list[dict[str, Any]] | None = None) -> list[tuple[float, float, str]]:
    duration = max(0.1, duration)
    groups: list[dict[str, Any]] = []
    for item in timed_segments or []:
        segment_text = str(item.get("text") or "").strip()
        if segment_text:
            groups.append({
                "text": segment_text,
                "duration": max(0.0, float(item.get("duration") or 0.0)),
                "weight": subtitle_timing_weight(segment_text),
            })
    if not groups:
        groups = [{"text": text, "duration": duration, "weight": subtitle_timing_weight(text)}]

    measured = [item for item in groups if item["duration"] > 0.05]
    measured_weight = sum(item["weight"] for item in measured)
    seconds_per_weight = (
        sum(item["duration"] for item in measured) / measured_weight
        if measured_weight else duration / max(1, sum(item["weight"] for item in groups))
    )
    raw_total = 0.0
    for item in groups:
        if item["duration"] <= 0.05:
            item["duration"] = seconds_per_weight * item["weight"]
        raw_total += item["duration"]
    scale = duration / max(0.1, raw_total)

    cues: list[tuple[float, float, str]] = []
    cursor = 0.0
    for group_index, group in enumerate(groups):
        group_duration = group["duration"] * scale
        group_end = duration if group_index == len(groups) - 1 else min(duration, cursor + group_duration)
        pieces = subtitle_chunks(group["text"]) or [group["text"]]
        total_weight = sum(subtitle_timing_weight(piece) for piece in pieces)
        piece_cursor = cursor
        for piece_index, piece in enumerate(pieces):
            if piece_index == len(pieces) - 1:
                piece_end = group_end
            else:
                piece_duration = group_duration * subtitle_timing_weight(piece) / max(1, total_weight)
                piece_end = min(group_end, piece_cursor + piece_duration)
            if piece_end > piece_cursor:
                cues.append((piece_cursor, piece_end, piece))
            piece_cursor = piece_end
        cursor = group_end
    return cues


_PYTHON_PACKAGE_CACHE: dict[tuple[str, str], bool] = {}


def python_has_package(python_exe: Path, package: str) -> bool:
    """探测某个 Python 环境里是否装了指定包（结果缓存，只探测一次）。"""
    key = (str(python_exe), package)
    if key not in _PYTHON_PACKAGE_CACHE:
        try:
            completed = subprocess.run(
                [str(python_exe), "-c", f"import {package}"],
                capture_output=True, timeout=120,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            _PYTHON_PACKAGE_CACHE[key] = completed.returncode == 0
        except Exception:
            _PYTHON_PACKAGE_CACHE[key] = False
    return _PYTHON_PACKAGE_CACHE[key]


def tool_python_candidates() -> list[Path]:
    """跑对齐/转写等工具脚本的 Python 候选：配置指定 > hdModule venv > VoxCPM venv。"""
    candidates: list[Path] = []
    override = config_path("toolPython", "LOCAL_DH_TOOL_PYTHON")
    if override:
        candidates.append(override)
    candidates.append(hd_venv_python())
    candidates.append(VOXCPM_PYTHON)
    return candidates


def find_python_with_package(package: str) -> Path | None:
    for candidate in tool_python_candidates():
        if candidate.is_file() and python_has_package(candidate, package):
            return candidate
    return None


def run_align_engine(python_exe: Path, script: Path, segments: list[str], part_paths: list[Path],
                     extra: dict | None = None) -> list[dict]:
    """跑一个字幕对齐子进程，返回对齐分段（[{"charCount", "timestamps"}]）。

    注意：不能把子进程输出接 PIPE 又不实时读取——FunASR/ModelScope/faster-whisper
    的日志和进度条会在 64KB 管道缓冲区写满后把子进程堵死（父进程 poll 永远等不到
    退出）。输出改写到日志文件，父进程只负责轮询退出码，结束后再读文件取最后一行 JSON。
    """
    request_path = TEMP_DIR / f"subtitle_align_{uuid.uuid4().hex}.json"
    payload: dict[str, Any] = {
        "ffmpeg": str(FFMPEG_EXE),
        "pairs": [
            {"audio": str(part.resolve()), "text": segment}
            for segment, part in zip(segments, part_paths)
        ],
    }
    if extra:
        payload.update(extra)
    request_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    log_path = TEMP_DIR / f"subtitle_align_{uuid.uuid4().hex}.log"
    try:
        with open(log_path, "w", encoding="utf-8", errors="replace") as log_file:
            process = subprocess.Popen(
                [str(python_exe), str(script), str(request_path)],
                cwd=str(APP_DIR),
                stdout=log_file, stderr=subprocess.STDOUT,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            deadline = time.time() + 1800
            while process.poll() is None:
                if MAIN_CANCEL.is_set():
                    kill_process_tree(process)
                    raise TaskCancelled("任务已手动停止。")
                if time.time() > deadline:
                    kill_process_tree(process)
                    raise TimeoutError("字幕对齐超时。")
                time.sleep(0.5)
        stdout_text = log_path.read_text(encoding="utf-8", errors="replace")
        output_lines = [line.strip() for line in stdout_text.splitlines() if line.strip()]
        result = json.loads(output_lines[-1]) if output_lines else {}
        if not result.get("ok"):
            raise RuntimeError(str(result.get("error") or "字幕对齐失败")[:300])
        aligned_segments = result.get("segments") or []
        if len(aligned_segments) != len(segments):
            raise RuntimeError("字幕对齐返回的分段数量不一致。")
        return aligned_segments
    finally:
        request_path.unlink(missing_ok=True)


def align_subtitle_cues(segments: list[str], part_paths: list[Path]) -> list[tuple[float, float, str]]:
    """逐字强制对齐，把字幕钉到真实发音上。

    优先用 Whisper large-v3-turbo（faster-whisper 词级时间戳 + 与文案做字符级
    锚定匹配，识别错字不影响对齐）；失败回退 FunASR 时间戳预测模型。
    两个引擎返回的时间戳都与「去除标点空白后的字符」一一对应，按字符流顺序
    直接切分给字幕分句即可。全部失败抛异常，由调用方回退到加权估算时间。
    """
    if not segments or not part_paths or len(segments) != len(part_paths):
        raise ValueError("字幕对齐缺少分段音频。")
    # 每个引擎各自挑一个装了对应依赖的 Python 环境（hdModule venv / VoxCPM venv /
    # 配置指定），都没有才算组件缺失。
    engines: list[tuple[str, Path, Path, dict | None]] = []
    if WHISPER_ALIGN_SCRIPT.is_file() and WHISPER_MODEL_DIR.is_dir():
        python_exe = find_python_with_package("faster_whisper")
        if python_exe:
            engines.append(("Whisper", python_exe, WHISPER_ALIGN_SCRIPT,
                            {"model_dir": str(WHISPER_MODEL_DIR)}))
    if ALIGN_SCRIPT.is_file():
        python_exe = find_python_with_package("funasr")
        if python_exe:
            engines.append(("FunASR", python_exe, ALIGN_SCRIPT, None))
    if not engines:
        raise RuntimeError("字幕对齐组件不存在（未安装对齐模型或可用的 Python 环境）。")
    aligned_segments: list[dict] | None = None
    last_error: Exception | None = None
    for engine_name, engine_python, engine_script, engine_extra in engines:
        try:
            aligned_segments = run_align_engine(engine_python, engine_script, segments,
                                                part_paths, engine_extra)
            if engine_name != engines[0][0]:
                append_job_log("main", f"字幕对齐已改用 {engine_name} 引擎。")
            break
        except TaskCancelled:
            raise
        except Exception as exc:  # noqa: BLE001 - 换下一个引擎
            last_error = exc
            append_job_log("main", f"字幕对齐引擎 {engine_name} 失败：{str(exc)[:200]}")
    if aligned_segments is None:
        raise RuntimeError(str(last_error or "字幕对齐失败")[:300])

    def clean_chars(value: str) -> str:
        return re.sub(r"[^\w一-鿿]+", "", value.lower())

    cues: list[tuple[float, float, str]] = []
    offset = 0.0
    for segment, part, aligned in zip(segments, part_paths, aligned_segments):
        part_duration = max(0.1, media_duration(part))
        segment_end = offset + part_duration
        timestamps = aligned.get("timestamps") or []
        script_clean = clean_chars(segment)
        pieces = subtitle_chunks(segment) or [segment]
        segment_cues: list[tuple[float, float, str]] | None = None
        if script_clean and len(timestamps) == len(script_clean):
            # 时间戳与净文本字符 1:1 顺序对应；每个字幕分句的净字符流
            # 恰好是段净字符流的顺序划分，直接按长度顺次切分。
            segment_cues = []
            position = 0
            for piece in pieces:
                piece_clean = clean_chars(piece)
                if not piece_clean:
                    continue
                if position + len(piece_clean) > len(timestamps):
                    segment_cues = None
                    break
                span = timestamps[position:position + len(piece_clean)]
                position += len(piece_clean)
                start = offset + span[0][0] / 1000.0
                end = offset + max(
                    span[-1][1] / 1000.0,
                    span[0][0] / 1000.0 + 0.3,
                )
                start = min(start, segment_end)
                end = min(end, segment_end)
                if end > start:
                    segment_cues.append((start, end, piece))
            if segment_cues is not None and position != len(timestamps):
                segment_cues = None
        if segment_cues is None:
            # 该段对齐不可靠：退回段内按权重分配（段边界仍然准确）
            total_weight = sum(subtitle_timing_weight(piece) for piece in pieces)
            piece_cursor = offset
            segment_cues = []
            for piece_index, piece in enumerate(pieces):
                piece_end = segment_end if piece_index == len(pieces) - 1 else min(
                    segment_end,
                    piece_cursor
                    + part_duration * subtitle_timing_weight(piece) / max(1, total_weight),
                )
                if piece_end > piece_cursor:
                    segment_cues.append((piece_cursor, piece_end, piece))
                piece_cursor = piece_end
        cues.extend(segment_cues)
        offset = segment_end
    return cues


def build_broll_windows(text: str, duration: float,
                        timed_segments: list[dict[str, Any]] | None = None,
                        cues: list[tuple[float, float, str]] | None = None) -> list[dict[str, Any]]:
    """Select spaced speech windows so B-roll supports the speaker instead of replacing them nonstop."""
    duration = max(0.0, float(duration))
    if duration < 4.0:
        return []
    cues = list(cues) if cues else build_subtitle_cues(text, duration, timed_segments)
    if not cues:
        return []
    lead = 1.5 if duration >= 9.0 else 0.0
    tail = 1.0 if duration >= 9.0 else 0.0
    usable_end = duration - tail
    next_allowed = lead
    windows: list[dict[str, Any]] = []
    cue_index = 0
    while cue_index < len(cues) and next_allowed + 4.0 <= usable_end:
        while cue_index < len(cues) and cues[cue_index][1] <= next_allowed:
            cue_index += 1
        if cue_index >= len(cues):
            break
        start = max(next_allowed, cues[cue_index][0])
        if start + 4.0 > usable_end:
            break
        query_parts: list[str] = []
        window_end = start
        scan_index = cue_index
        while scan_index < len(cues) and cues[scan_index][0] < start + 7.0:
            cue_start, cue_end, cue_text = cues[scan_index]
            if cue_end > start:
                query_parts.append(cue_text)
                window_end = max(window_end, min(usable_end, start + 7.0, cue_end))
                if window_end - start >= 5.2:
                    break
            scan_index += 1
        if window_end - start < 4.0:
            window_end = min(usable_end, start + 4.0)
        clip_duration = max(4.0, min(7.0, window_end - start))
        window_end = start + clip_duration
        query = re.sub(r"\s+", " ", "".join(query_parts)).strip() or text[:80]
        windows.append({
            "timelineStart": round(start, 3),
            "timelineEnd": round(window_end, 3),
            "duration": round(clip_duration, 3),
            "query": query,
        })
        # Keep the talking head visible between inserts and avoid a wall of continuous B-roll.
        next_allowed = window_end + 5.0
        cue_index = max(cue_index + 1, scan_index + 1)
    return windows


def run_local_broll_matcher(queries: list[str]) -> list[dict[str, Any]]:
    if not queries:
        return []
    python_exe = hd_venv_python()
    if not python_exe.is_file() or not BROLL_MATCHER.is_file():
        raise RuntimeError("本地素材匹配组件不存在。")
    if not BROLL_INDEX.is_file() or not (BROLL_MODEL_DIR / "model.safetensors").is_file():
        raise RuntimeError("本地素材库或文案理解模型不存在。")
    request_path = TEMP_DIR / f"broll_match_{uuid.uuid4().hex}.json"
    request_path.write_text(json.dumps({
        "catalogPath": str(BROLL_INDEX),
        "modelPath": str(BROLL_MODEL_DIR),
        "cachePath": str(BROLL_EMBEDDING_CACHE),
        "queries": queries,
        "topK": 10,
        "requireSafeShots": True,
    }, ensure_ascii=False), encoding="utf-8")
    try:
        completed = subprocess.run(
            [str(python_exe), str(BROLL_MATCHER), str(request_path)],
            cwd=str(APP_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout or "素材匹配失败")[-600:])
        output_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        if not output_lines:
            raise RuntimeError("素材匹配模型没有返回结果。")
        return list(json.loads(output_lines[-1]).get("matches") or [])
    finally:
        request_path.unlink(missing_ok=True)


def plan_broll_segments(kind: str, text: str, duration: float,
                        timed_segments: list[dict[str, Any]] | None = None,
                        person_id: str = "",
                        cues: list[tuple[float, float, str]] | None = None) -> list[dict[str, Any]]:
    windows = build_broll_windows(text, duration, timed_segments, cues=cues)
    if not windows:
        append_job_log(kind, "成片不足可用插入时长，本次不添加智能素材。")
        return []
    update_job(kind, stage="正在理解文案并匹配素材", progress=47)
    catalog = json.loads(BROLL_INDEX.read_text(encoding="utf-8"))
    asset_by_id = {
        str(item.get("id") or ""): item
        for item in catalog.get("assets") or []
        if item.get("useMode") == "ready" and item.get("safeShots")
    }
    matches = run_local_broll_matcher([window["query"] for window in windows])
    used_ids: set[str] = set()
    planned: list[dict[str, Any]] = []
    for window, match in zip(windows, matches):
        duration_needed = max(4.0, min(7.0, float(window["duration"])))
        selected_asset: dict[str, Any] | None = None
        selected_match: dict[str, Any] | None = None
        selected_shot: dict[str, Any] | None = None
        selected_duration = duration_needed
        candidates = match.get("items") or []
        if person_id:
            person_candidates = [
                candidate for candidate in candidates
                if str((asset_by_id.get(str(candidate.get("id") or "")) or {}).get("personId") or "")
                == person_id
            ]
            if person_candidates:
                candidates = person_candidates
        for candidate in candidates:
            asset_id = str(candidate.get("id") or "")
            asset = asset_by_id.get(asset_id)
            if asset is None or asset_id in used_ids:
                continue
            path = Path(str(asset.get("path") or ""))
            shots = [
                shot for shot in asset.get("safeShots") or []
                if float(shot.get("safeDuration") or 0.0) + 0.01 >= 4.0
            ]
            if not path.is_file() or not shots:
                continue
            selected_asset = asset
            selected_match = candidate
            selected_shot = max(shots, key=lambda shot: float(shot.get("safeDuration") or 0.0))
            selected_duration = max(
                4.0,
                min(duration_needed, 7.0, float(selected_shot.get("safeDuration") or 0.0)),
            )
            break
        if selected_asset is None or selected_match is None or selected_shot is None:
            append_job_log(kind, f"没有找到满足 {duration_needed:.1f} 秒安全区间的素材：{window['query'][:36]}")
            continue
        asset_id = str(selected_asset.get("id") or "")
        used_ids.add(asset_id)
        duration_needed = selected_duration
        safe_start = float(selected_shot["safeStart"])
        safe_duration = float(selected_shot["safeDuration"])
        spare = max(0.0, safe_duration - duration_needed)
        digest = hashlib.sha256(f"{asset_id}|{window['query']}".encode("utf-8")).hexdigest()
        offset_ratio = 0.25 + (int(digest[:8], 16) / 0xFFFFFFFF) * 0.5
        source_start = safe_start + spare * offset_ratio
        source_end = source_start + duration_needed
        planned.append({
            "assetId": asset_id,
            "path": str(selected_asset["path"]),
            "timelineStart": round(float(window["timelineStart"]), 3),
            "timelineEnd": round(float(window["timelineStart"]) + duration_needed, 3),
            "duration": round(duration_needed, 3),
            "sourceStart": round(source_start, 3),
            "sourceEnd": round(source_end, 3),
            "fadeSeconds": 0.75,
            "query": window["query"],
            "visualSummary": str(selected_asset.get("visualSummary") or ""),
            "score": float(selected_match.get("score") or 0.0),
            "audioMuted": True,
            "fillMode": "cover",
        })
        append_job_log(
            kind,
            f"智能素材 {format_duration(float(window['timelineStart']))}："
            f"{selected_asset.get('visualSummary') or selected_asset.get('filename')} "
            f"({duration_needed:.1f}秒，匹配度 {float(selected_match.get('score') or 0.0):.3f})",
        )
    plan_path = BROLL_DIR / "last-plan.json"
    plan_path.write_text(json.dumps({
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scriptHash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "duration": round(float(duration), 3),
        "rules": {
            "clipSeconds": [4.0, 7.0],
            "fadeSeconds": 0.75,
            "sourceAudio": "muted",
            "fillMode": "cover",
        },
        "segments": planned,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_job(kind, stage=f"已匹配 {len(planned)} 段智能素材", progress=49)
    return planned


def ass_timestamp(seconds: float) -> str:
    centiseconds = max(0, int(round(seconds * 100)))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cents = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cents:02d}"


def ass_escape(text: str) -> str:
    return (
        text.replace("\\", "＼").replace("{", "｛").replace("}", "｝")
        .replace("\r\n", "\\N").replace("\r", "\\N").replace("\n", "\\N")
    )


def normalize_hex_color(value: Any, fallback: str = "#FFE66D") -> str:
    color = str(value or "").strip().upper()
    return color if re.fullmatch(r"#[0-9A-F]{6}", color) else fallback


def normalize_video_title(value: Any, limit: int = 80) -> str:
    """Replace punctuation/symbols with spaces for overlays, covers and files."""
    cleaned = "".join(
        " " if unicodedata.category(character)[:1] in {"P", "S"} else character
        for character in str(value or "")
    )
    return re.sub(r"\s+", " ", cleaned).strip()[:limit].rstrip()


def ass_color(value: Any, fallback: str = "#FFE66D") -> str:
    color = normalize_hex_color(value, fallback)[1:]
    red, green, blue = color[0:2], color[2:4], color[4:6]
    return f"&H00{blue}{green}{red}"


def ass_override_color(value: Any, fallback: str) -> str:
    color = normalize_hex_color(value, fallback)[1:]
    red, green, blue = color[0:2], color[2:4], color[4:6]
    return f"&H{blue}{green}{red}&"


def normalize_speaker_name(value: Any) -> str:
    name = re.sub(r"\s+", " ", str(value or "")).strip()[:40]
    if name in {"张廷伟", "张廷炜", "张霆伟"}:
        return "讲师A"
    return name


def create_text_overlay_ass(settings: dict[str, Any], duration: float,
                            width: int, height: int) -> Path | None:
    title = str(settings.get("title") or "").strip()
    if width > height:
        # 横版（16:9 / 4:3）数字人不加标题，字幕走底部居中的电影位置
        title = ""
    subtitles_enabled = bool(settings.get("subtitles"))
    text = str(settings.get("text") or "").strip()
    nameplate_enabled = bool(settings.get("nameplate"))
    speaker_name = normalize_speaker_name(settings.get("speakerName"))
    speaker_details = str(settings.get("speakerDetails") or "").strip()
    has_nameplate = nameplate_enabled and bool(speaker_name or speaker_details)
    if not title and (not subtitles_enabled or not text) and not has_nameplate:
        return None

    font_name = TEXT_FONTS.get(
        str(settings.get("font") or "dongfangdakai"), TEXT_FONTS["dongfangdakai"]
    )
    shadow_level = TEXT_SHADOWS.get(
        str(settings.get("shadow") or "standard"), TEXT_SHADOWS["standard"]
    )
    title_top_color = ass_color(settings.get("titleColorTop"), "#FFFFFF")
    title_bottom_color = ass_color(settings.get("titleColorBottom"), "#FFE66D")
    title_top_override = ass_override_color(settings.get("titleColorTop"), "#FFFFFF")
    title_bottom_override = ass_override_color(settings.get("titleColorBottom"), "#FFE66D")
    base_edge = min(width, height)
    portrait = height > width
    if portrait:
        title_size = max(40, int(round(base_edge * 0.084)))
        subtitle_size = max(32, int(round(base_edge * 0.063)))
        name_size = max(34, int(round(base_edge * 0.066)))
        details_size = max(20, int(round(base_edge * 0.031)))
        horizontal_margin = max(24, int(round(width * 0.065)))
        subtitle_horizontal_margin = max(42, int(round(width * 0.12)))
        title_margin = max(28, int(round(height * 0.072)))
        subtitle_margin = max(34, int(round(height * 0.315)))
        name_margin = max(32, int(round(height * 0.455)))
    else:
        # 横版：字幕字号比电影规格（约 4% 短边）略大，手机上也能看清
        title_size = max(38, int(round(base_edge * 0.065)))
        subtitle_size = max(30, int(round(base_edge * 0.046)))
        name_size = max(30, int(round(base_edge * 0.045)))
        details_size = max(18, int(round(base_edge * 0.023)))
        horizontal_margin = max(24, int(round(width * 0.055)))
        subtitle_horizontal_margin = max(36, int(round(width * 0.08)))
        title_margin = max(28, int(round(height * 0.055)))
        subtitle_margin = max(34, int(round(height * 0.065)))
        name_margin = max(30, int(round(height * 0.50)))
    details_margin = name_margin + int(round(name_size * 1.18))
    blur_by_level = {0: 0, 1: 2, 2: 4, 4: 7}
    blur = blur_by_level.get(shadow_level, 4)
    shadow_primary = "&H68000000" if shadow_level < 4 else "&H50000000"

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Title,{font_name},{title_size},{title_top_color},{title_bottom_color},&H00141418,&H00000000,"
        f"-1,0,0,0,100,100,1,0,1,0,0,8,{horizontal_margin},{horizontal_margin},{title_margin},1",
        f"Style: Subtitle,{font_name},{subtitle_size},&H00FFFFFF,&H00FFFFFF,&H00141418,&H70000000,"
        f"0,0,0,0,100,100,0,0,1,0,0,2,{subtitle_horizontal_margin},{subtitle_horizontal_margin},{subtitle_margin},1",
        f"Style: Name,{font_name},{name_size},&H00FFFFFF,&H00FFFFFF,&H00141418,&H00000000,"
        f"-1,0,0,0,100,100,1,0,1,0,0,7,{horizontal_margin},{horizontal_margin},{name_margin},1",
        f"Style: Details,{font_name},{details_size},&H00FFFFFF,&H00FFFFFF,&H00141418,&H00000000,"
        f"0,0,0,0,100,100,0,0,1,0,0,7,{horizontal_margin},{horizontal_margin},{details_margin},1",
        f"Style: TitleShadow,{font_name},{title_size},{shadow_primary},{shadow_primary},&H00000000,&H00000000,"
        f"-1,0,0,0,100,100,1,0,1,0,0,8,{horizontal_margin},{horizontal_margin},{title_margin},1",
        f"Style: SubtitleShadow,{font_name},{subtitle_size},{shadow_primary},{shadow_primary},&H00000000,&H00000000,"
        f"0,0,0,0,100,100,0,0,1,0,0,2,{subtitle_horizontal_margin},{subtitle_horizontal_margin},{subtitle_margin},1",
        f"Style: NameShadow,{font_name},{name_size},{shadow_primary},{shadow_primary},&H00000000,&H00000000,"
        f"-1,0,0,0,100,100,1,0,1,0,0,7,{horizontal_margin},{horizontal_margin},{name_margin},1",
        f"Style: DetailsShadow,{font_name},{details_size},{shadow_primary},{shadow_primary},&H00000000,&H00000000,"
        f"0,0,0,0,100,100,0,0,1,0,0,7,{horizontal_margin},{horizontal_margin},{details_margin},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    def add_text_event(start: float, end: float, style: str, value: str,
                       fade_milliseconds: int = 0) -> None:
        escaped = ass_escape(value)
        start_time = ass_timestamp(start)
        end_time = ass_timestamp(end)
        fade_override = (
            f"\\fad({fade_milliseconds},{fade_milliseconds})"
            if fade_milliseconds > 0 else ""
        )
        if shadow_level > 0:
            lines.append(
                f"Dialogue: 0,{start_time},{end_time},{style}Shadow,,0,0,0,,"
                f"{{{fade_override}\\blur{blur}}}{escaped}"
            )
        main_override = f"{{{fade_override}}}" if fade_override else ""
        lines.append(
            f"Dialogue: 1,{start_time},{end_time},{style},,0,0,0,,{main_override}{escaped}"
        )

    if title:
        formatted_title = format_title_lines(title[:80])
        title_parts = formatted_title.split("\n", 1)
        if len(title_parts) == 2:
            colored_title = (
                f"{{\\1c{title_top_override}}}{ass_escape(title_parts[0])}\\N"
                f"{{\\1c{title_bottom_override}}}{ass_escape(title_parts[1])}"
            )
        else:
            colored_title = f"{{\\1c{title_bottom_override}}}{ass_escape(formatted_title)}"
        if shadow_level > 0:
            lines.append(
                f"Dialogue: 0,0:00:00.00,{ass_timestamp(duration)},TitleShadow,,0,0,0,,"
                f"{{\\blur{blur}}}{ass_escape(formatted_title)}"
            )
        lines.append(
            f"Dialogue: 1,0:00:00.00,{ass_timestamp(duration)},Title,,0,0,0,,{colored_title}"
        )
    if subtitles_enabled and text:
        precise_cues = settings.get("cues") if isinstance(settings.get("cues"), list) else []
        if precise_cues:
            for start, end, cue_text in precise_cues:
                display_text = subtitle_display_text(str(cue_text))
                if display_text:
                    add_text_event(float(start), float(end), "Subtitle", display_text)
        else:
            timed_segments = settings.get("segments") if isinstance(settings.get("segments"), list) else []
            for start, end, cue_text in build_subtitle_cues(text, duration, timed_segments):
                display_text = subtitle_display_text(cue_text)
                if display_text:
                    add_text_event(start, end, "Subtitle", display_text)
    if has_nameplate:
        detail_lines = []
        for raw_line in speaker_details.splitlines():
            value = raw_line.strip()
            if value:
                detail_lines.append(value if value.startswith(("·", "•")) else f"· {value}")
        formatted_details = "\n".join(detail_lines)
        broll_intervals = [
            (
                max(0.0, float(item.get("timelineStart") or 0.0)),
                min(duration, float(item.get("timelineEnd") or 0.0)),
            )
            for item in settings.get("brollSegments") or []
            if isinstance(item, dict)
        ]
        appearance = 0.0
        while appearance < duration:
            disappearance = min(duration, appearance + 3.0)
            overlaps_broll = any(
                interval_start < disappearance and interval_end > appearance
                for interval_start, interval_end in broll_intervals
            )
            if not overlaps_broll:
                if speaker_name:
                    add_text_event(
                        appearance, disappearance, "Name", speaker_name[:40], fade_milliseconds=500
                    )
                if formatted_details:
                    add_text_event(
                        appearance, disappearance, "Details", formatted_details[:300],
                        fade_milliseconds=500,
                    )
            appearance += 15.0
    overlay_path = TEMP_DIR / f"text_overlay_{uuid.uuid4().hex}.ass"
    overlay_path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return overlay_path


def prepare_background_music(kind: str, source: Path, target_duration: float) -> Path:
    target_duration = max(0.1, float(target_duration))
    token = uuid.uuid4().hex
    seed_path = TEMP_DIR / f"music_seed_{token}.wav"
    current_path = seed_path
    prepared_path = TEMP_DIR / f"music_ready_{token}.wav"
    temporary_paths: list[Path] = [seed_path]

    def run_audio_command(command: list[str], failure_message: str) -> None:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3600,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode != 0:
            raise RuntimeError(f"{failure_message}{completed.stderr[-500:]}")

    try:
        update_job(kind, stage="正在整理背景音乐", progress=96.8)
        run_audio_command(
            [
                str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(source),
                "-vn", "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le", str(seed_path),
            ],
            "背景音乐读取失败。",
        )
        seed_duration = media_duration(seed_path)
        if seed_duration <= 0.1:
            raise RuntimeError("背景音乐没有可读取的音频。")

        current_duration = seed_duration
        crossfade_duration = min(3.5, max(0.25, seed_duration / 3))
        looped = False
        pass_index = 0
        while current_duration < target_duration:
            pass_index += 1
            looped = True
            next_path = TEMP_DIR / f"music_loop_{token}_{pass_index}.wav"
            temporary_paths.append(next_path)
            active_crossfade = min(crossfade_duration, max(0.1, current_duration / 3))
            run_audio_command(
                [
                    str(FFMPEG_EXE), "-loglevel", "error", "-y",
                    "-i", str(current_path), "-i", str(current_path),
                    "-filter_complex",
                    f"[0:a][1:a]acrossfade=d={active_crossfade:.3f}:c1=tri:c2=tri[a]",
                    "-map", "[a]", "-ac", "2", "-ar", "44100",
                    "-c:a", "pcm_s16le", str(next_path),
                ],
                "背景音乐首尾衔接失败。",
            )
            current_path = next_path
            current_duration = media_duration(current_path)
            if current_duration <= 0.1:
                raise RuntimeError("背景音乐首尾衔接后没有生成有效音频。")

        edge_fade = min(3.0, target_duration / 2)
        fade_out_start = max(0.0, target_duration - edge_fade)
        final_filter = (
            f"atrim=duration={target_duration:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={edge_fade:.3f},"
            f"afade=t=out:st={fade_out_start:.3f}:d={edge_fade:.3f}"
        )
        run_audio_command(
            [
                str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(current_path),
                "-af", final_filter, "-t", f"{target_duration:.3f}",
                "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le", str(prepared_path),
            ],
            "背景音乐渐入渐出处理失败。",
        )
        if not prepared_path.is_file() or prepared_path.stat().st_size <= 44:
            raise RuntimeError("背景音乐渐入渐出处理后没有生成有效音频。")
        if looped:
            append_job_log(
                kind,
                f"背景音乐不足成片长度，已首尾交叉衔接；交叉渐变 {crossfade_duration:.1f} 秒，"
                f"视频首尾各渐变 {edge_fade:.1f} 秒。",
            )
        else:
            append_job_log(kind, f"背景音乐已按成片截取，视频首尾各渐变 {edge_fade:.1f} 秒。")
        return prepared_path
    except Exception:
        prepared_path.unlink(missing_ok=True)
        raise
    finally:
        for path in temporary_paths:
            if path != prepared_path:
                path.unlink(missing_ok=True)


def export_resolution(kind: str, source: Path, destination: Path, resolution: str,
                      source_dimensions: tuple[int, int] | None = None,
                      text_settings: dict[str, Any] | None = None) -> Path:
    if not FFMPEG_EXE.exists():
        raise RuntimeError("没有找到高清视频导出组件。")
    source_info = video_info(source)
    width, height = int(source_info["width"]), int(source_info["height"])
    source_duration = max(0.1, float(source_info.get("duration") or 0.1))
    broll_segments: list[dict[str, Any]] = []
    for raw_segment in (text_settings or {}).get("brollSegments") or []:
        if not isinstance(raw_segment, dict):
            continue
        broll_path = Path(str(raw_segment.get("path") or ""))
        timeline_start = max(0.0, float(raw_segment.get("timelineStart") or 0.0))
        requested_duration = max(0.0, float(raw_segment.get("duration") or 0.0))
        duration_value = min(7.0, requested_duration, source_duration - timeline_start)
        source_start = max(0.0, float(raw_segment.get("sourceStart") or 0.0))
        if not broll_path.is_file() or duration_value < 4.0:
            continue
        fade_seconds = max(0.5, min(1.0, float(raw_segment.get("fadeSeconds") or 0.75)))
        broll_segments.append({
            **raw_segment,
            "path": broll_path,
            "timelineStart": timeline_start,
            "timelineEnd": timeline_start + duration_value,
            "duration": duration_value,
            "sourceStart": source_start,
            "fadeSeconds": min(fade_seconds, duration_value / 2),
        })
    music_value = str((text_settings or {}).get("musicPath") or "").strip()
    music_path = Path(music_value) if music_value else None
    if music_path is not None and not music_path.is_file():
        raise ValueError("选择的背景音乐文件已经不存在。")
    raw_render_music_volume = (text_settings or {}).get("musicVolume", 0.12)
    music_volume = max(0.0, min(0.30, float(raw_render_music_volume)))
    if resolution == "source" and source_dimensions:
        source_target_width, source_target_height = source_dimensions
        source_long = min(3840, max(source_target_width, source_target_height))
        scale = source_long / max(source_target_width, source_target_height)
        target_width = max(2, int(round(source_target_width * scale / 2) * 2))
        target_height = max(2, int(round(source_target_height * scale / 2) * 2))
        stage = "正在恢复原视频分辨率"
    elif resolution == "source":
        target_width, target_height = width, height
        stage = "正在保存视频"
    else:
        target_long = 2560 if resolution == "2k" else 3840
        scale = target_long / max(width, height)
        target_width = max(2, int(round(width * scale / 2) * 2))
        target_height = max(2, int(round(height * scale / 2) * 2))
        stage = f"正在导出{resolution.upper()}视频"

    overlay_path = create_text_overlay_ass(
        text_settings or {}, source_duration, target_width, target_height
    ) if text_settings else None
    render_parts = []
    if overlay_path is not None:
        if str((text_settings or {}).get("title") or "").strip():
            render_parts.append("标题")
        if (text_settings or {}).get("subtitles") and str((text_settings or {}).get("text") or "").strip():
            render_parts.append("字幕")
        if (text_settings or {}).get("nameplate"):
            render_parts.append("人名资料")
    if music_path is not None:
        render_parts.append("背景音乐")
    if broll_segments:
        render_parts.append("智能素材")
    if render_parts:
        render_stage = f"正在添加{'、'.join(render_parts)}"
        if resolution in {"2k", "4k"}:
            stage = f"{render_stage}并导出{resolution.upper()}视频"
        elif (width, height) != (target_width, target_height):
            stage = f"{render_stage}并恢复原视频分辨率"
        else:
            stage = render_stage

    if (
        (width, height) == (target_width, target_height)
        and overlay_path is None
        and music_path is None
        and not broll_segments
    ):
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        return destination
    prepared_music_path: Path | None = None
    render_music_path = music_path
    if music_path is not None:
        prepared_music_path = prepare_background_music(kind, music_path, source_duration)
        render_music_path = prepared_music_path
    update_job(kind, stage=f"{stage} 0%", progress=97)

    base_video_filters = [f"scale={target_width}:{target_height}:flags=lanczos", "setsar=1"]
    if broll_segments:
        input_args = [str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(source)]
        complex_filters = [f"[0:v]{','.join(base_video_filters)}[base]"]
        current_label = "base"
        for broll_index, segment in enumerate(broll_segments, start=1):
            input_args.extend(["-i", str(segment["path"])])
            duration_value = float(segment["duration"])
            fade_seconds = float(segment["fadeSeconds"])
            timeline_start = float(segment["timelineStart"])
            timeline_end = float(segment["timelineEnd"])
            fade_out_start = max(0.0, duration_value - fade_seconds)
            complex_filters.append(
                f"[{broll_index}:v]trim=start={float(segment['sourceStart']):.3f}:"
                f"duration={duration_value:.3f},setpts=PTS-STARTPTS,"
                f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={target_width}:{target_height},setsar=1,format=rgba,"
                f"fade=t=in:st=0:d={fade_seconds:.3f}:alpha=1,"
                f"fade=t=out:st={fade_out_start:.3f}:d={fade_seconds:.3f}:alpha=1,"
                f"setpts=PTS+{timeline_start:.3f}/TB[broll{broll_index}]"
            )
            next_label = f"composite{broll_index}"
            complex_filters.append(
                f"[{current_label}][broll{broll_index}]overlay=x=0:y=0:"
                f"eof_action=pass:shortest=0:enable='between(t\\,{timeline_start:.3f}\\,{timeline_end:.3f})'"
                f"[{next_label}]"
            )
            current_label = next_label
        if overlay_path is not None:
            complex_filters.append(
                f"[{current_label}]ass={overlay_path.name}:fontsdir=../data/fonts[vout]"
            )
        else:
            complex_filters.append(f"[{current_label}]null[vout]")
        if render_music_path is not None:
            music_input_index = len(broll_segments) + 1
            input_args.extend(["-i", str(render_music_path)])
            complex_filters.extend([
                "[0:a]aresample=async=1:first_pts=0[voice]",
                f"[{music_input_index}:a]volume={music_volume:.3f},"
                "aresample=async=1:first_pts=0[music]",
                "[voice][music]amix=inputs=2:duration=first:"
                "dropout_transition=2:normalize=0[amixed]",
                f"[amixed]{EXPORT_AUDIO_FILTER}[aout]",
            ])
            common = input_args + [
                "-filter_complex", ";".join(complex_filters),
                "-map", "[vout]", "-map", "[aout]",
            ]
        else:
            # B-roll audio streams are intentionally never mapped into the result.
            complex_filters.append(
                f"[0:a]aresample=async=1:first_pts=0,{EXPORT_AUDIO_FILTER}[aout]"
            )
            common = input_args + [
                "-filter_complex", ";".join(complex_filters),
                "-map", "[vout]", "-map", "[aout]",
            ]
    else:
        filters = list(base_video_filters)
        if overlay_path is not None:
            filters.append(f"ass={overlay_path.name}:fontsdir=../data/fonts")
        video_filters = ",".join(filters)
        if render_music_path is not None:
            filter_complex = (
                f"[0:v]{video_filters}[vout];"
                f"[0:a]aresample=async=1:first_pts=0[voice];"
                f"[1:a]volume={music_volume:.3f},aresample=async=1:first_pts=0[music];"
                f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[amixed];"
                f"[amixed]{EXPORT_AUDIO_FILTER}[aout]"
            )
            common = [
                str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(source),
                "-i", str(render_music_path),
                "-filter_complex", filter_complex,
                "-map", "[vout]", "-map", "[aout]",
            ]
        else:
            common = [
                str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(source),
                "-vf", video_filters,
                "-af", EXPORT_AUDIO_FILTER,
            ]
    encoders = [
        ["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-b:v", "0"],
        ["-c:v", "libx264", "-preset", "medium", "-crf", "18"],
    ]
    last_error = ""
    progress_path = TEMP_DIR / f"ffmpeg_progress_{uuid.uuid4().hex}.txt"
    try:
        for encoder_index, encoder in enumerate(encoders):
            destination.unlink(missing_ok=True)
            progress_path.unlink(missing_ok=True)
            command = common + encoder + [
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "-progress", str(progress_path), "-nostats", str(destination),
            ]
            process = subprocess.Popen(
                command,
                cwd=str(overlay_path.parent) if overlay_path is not None else None,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            encode_started = time.time()
            last_reported = -1
            timed_out = False
            while process.poll() is None:
                if MAIN_CANCEL.is_set():
                    kill_process_tree(process)
                    raise TaskCancelled("任务已手动停止。")
                if time.time() - encode_started > 7200:
                    timed_out = True
                    kill_process_tree(process)
                    break
                try:
                    progress_text = progress_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    progress_text = ""
                matches = re.findall(r"out_time_(?:us|ms)=(\d+)", progress_text)
                if matches:
                    output_seconds = int(matches[-1]) / 1_000_000
                    percent = max(0, min(100, output_seconds / source_duration * 100))
                    rounded = int(percent)
                    if rounded != last_reported:
                        elapsed = time.time() - encode_started
                        eta = elapsed * (100 - percent) / percent if percent >= 1 else 0
                        detail = (
                            f"{stage} {rounded}% · "
                            f"{format_duration(output_seconds)}/{format_duration(source_duration)}"
                        )
                        if eta > 0:
                            detail += f" · 预计剩余 {format_duration(eta)}"
                        update_job(kind, stage=detail, progress=round(97 + percent * 0.02, 1))
                        last_reported = rounded
                time.sleep(0.7)
            try:
                _, stderr = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                kill_process_tree(process)
                _, stderr = process.communicate(timeout=5)
            if not timed_out and process.returncode == 0 and destination.is_file() and destination.stat().st_size > 0:
                update_job(kind, stage=f"{stage} 100% · 正在保存", progress=99.5)
                return destination
            last_error = (stderr or "导出超时" if timed_out else stderr or "导出失败")[-800:]
            destination.unlink(missing_ok=True)
            if encoder_index + 1 < len(encoders):
                update_job(kind, stage=f"{stage} · 正在切换兼容模式", progress=97)
    finally:
        progress_path.unlink(missing_ok=True)
        if overlay_path is not None:
            overlay_path.unlink(missing_ok=True)
        if prepared_music_path is not None:
            prepared_music_path.unlink(missing_ok=True)
    raise RuntimeError(f"{resolution.upper()}视频导出失败。{last_error}")


def output_title_stem(title: Any, fallback_text: Any = "") -> str:
    stem = normalize_video_title(title, 64) or normalize_video_title(fallback_text, 36) or "未命名视频"
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip(" .") or "未命名视频"
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
    if stem.upper() in reserved:
        stem += " 视频"
    return stem


def unique_output_path(directory: Path, stem: str, suffix: str) -> Path:
    candidate = directory / f"{stem}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def split_cover_title_lines(title: str) -> list[str]:
    title = normalize_video_title(title)
    if not title:
        return []
    if subtitle_visual_units(title) <= 11:
        return [title]
    tokens = [token for token in semantic_text_tokens(title) if token]
    total = subtitle_visual_units(title)
    running = 0.0
    candidates: list[tuple[float, int]] = []
    for index, token in enumerate(tokens[:-1], start=1):
        running += subtitle_visual_units(token)
        left = "".join(tokens[:index]).strip()
        right = "".join(tokens[index:]).strip()
        if left and right:
            previous_token = tokens[index - 1]
            next_token = tokens[index]
            boundary_score = abs(running - total / 2)
            # Spaces in the cleaned title mark former punctuation and are the
            # strongest natural two-line break candidates.
            if previous_token.isspace() or next_token.isspace():
                boundary_score -= 4.0
            previous_word = re.sub(r"[^\w\u3400-\u9fff]", "", previous_token)
            next_word = re.sub(r"[^\w\u3400-\u9fff]", "", next_token)
            if re.fullmatch(r"[\u3400-\u9fff]", previous_word or ""):
                boundary_score += 2.5
            if re.fullmatch(r"[\u3400-\u9fff]", next_word or ""):
                boundary_score += 2.5
            if previous_word in {"把", "被", "让", "将", "和", "与", "或", "的", "地", "得"}:
                boundary_score += 4.0
            candidates.append((boundary_score, index))
    if candidates:
        _, split_at = min(candidates, key=lambda item: item[0])
        lines = ["".join(tokens[:split_at]).strip(), "".join(tokens[split_at:]).strip()]
        if all(lines):
            return lines
    midpoint = max(1, len(title) // 2)
    return [title[:midpoint].strip(), title[midpoint:].strip()]


def cover_inward_arm_score(analysis: Any, face: tuple[int, int, int, int], cv2: Any, np: Any) -> float:
    """Estimate whether hands/forearms are cramped around the face or chest."""
    frame_height, frame_width = analysis.shape[:2]
    x, y, face_width, face_height = face
    face_center_x = x + face_width / 2
    face_bottom = y + face_height
    ycrcb = cv2.cvtColor(analysis, cv2.COLOR_BGR2YCrCb)
    # A conventional YCrCb skin range works well as a lightweight hand/forearm
    # detector. The face is masked out before measuring the upper torso.
    skin = cv2.inRange(
        ycrcb,
        np.array((35, 132, 72), dtype=np.uint8),
        np.array((255, 180, 138), dtype=np.uint8),
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, kernel)
    face_left = max(0, x - int(face_width * 0.12))
    face_top = max(0, y - int(face_height * 0.10))
    face_right = min(frame_width, x + face_width + int(face_width * 0.12))
    face_lower = min(frame_height, y + face_height + int(face_height * 0.18))
    skin[face_top:face_lower, face_left:face_right] = 0

    zone_left = max(0, int(round(face_center_x - face_width * 1.55)))
    zone_right = min(frame_width, int(round(face_center_x + face_width * 1.55)))
    zone_top = max(0, int(round(y + face_height * 0.72)))
    zone_bottom = min(frame_height, int(round(face_bottom + face_height * 2.15)))
    zone = np.zeros_like(skin)
    zone[zone_top:zone_bottom, zone_left:zone_right] = skin[zone_top:zone_bottom, zone_left:zone_right]

    component_count, _, stats, centroids = cv2.connectedComponentsWithStats(zone, connectivity=8)
    face_area = max(1.0, float(face_width * face_height))
    score = 0.0
    raised_sides: set[str] = set()
    for component_index in range(1, component_count):
        area = float(stats[component_index, cv2.CC_STAT_AREA])
        area_ratio = area / face_area
        if area_ratio < 0.012 or area_ratio > 1.65:
            continue
        center_x, center_y = [float(value) for value in centroids[component_index]]
        horizontal_distance = abs(center_x - face_center_x) / max(1.0, face_width)
        vertical_distance = (center_y - face_bottom) / max(1.0, face_height)
        if vertical_distance < -0.25 or horizontal_distance > 1.65:
            continue
        horizontal_weight = max(0.0, 1.55 - horizontal_distance) / 1.55
        if vertical_distance <= 0.90:
            vertical_weight = 1.0
        else:
            vertical_weight = max(0.0, 2.15 - vertical_distance) / 1.25 * 0.48
        score += min(0.85, area_ratio) * horizontal_weight * vertical_weight
        if vertical_distance <= 0.95 and horizontal_distance <= 1.35:
            raised_sides.add("left" if center_x < face_center_x else "right")
    # Two hands converging toward the torso is the strongest sign of the
    # contracted, awkward pose the cover should avoid.
    if len(raised_sides) >= 2:
        score += 0.42
    return max(0.0, score)


def select_cover_frame(kind: str, avatar_path: Path) -> tuple[Any, tuple[int, int, int, int] | None, float, bool, float]:
    """Choose a random high-quality, frontal, open-eye frame from the avatar video."""
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("封面画面筛选组件没有安装。") from exc

    capture = cv2.VideoCapture(str(avatar_path))
    if not capture.isOpened():
        raise RuntimeError("封面无法读取数字人形象视频。")
    fps = max(1.0, float(capture.get(cv2.CAP_PROP_FPS) or 25.0))
    frame_count = max(1, int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 1))
    duration = frame_count / fps
    margin = min(max(2, int(round(fps * 1.5))), max(0, frame_count // 4))
    first = margin
    last = max(first, frame_count - margin - 2)
    available = max(1, last - first + 1)
    # Fourteen random candidates reliably avoid blinks while keeping the
    # post-export cover step reasonably quick on long avatar videos.
    sample_count = min(14, available)
    positions = random.sample(range(first, last + 1), sample_count) if available > sample_count else list(range(first, last + 1))

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    if face_cascade.empty() or eye_cascade.empty():
        capture.release()
        raise RuntimeError("封面人脸检测组件无法加载。")

    candidates: list[dict[str, Any]] = []
    sharp_fallbacks: list[dict[str, Any]] = []
    for position_index, frame_index in enumerate(positions, start=1):
        capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_index - 1))
        ok_previous, previous = capture.read()
        ok_current, frame = capture.read()
        ok_next, following = capture.read()
        if not ok_current or frame is None:
            continue
        frame_height, frame_width = frame.shape[:2]
        analysis_scale = min(1.0, 720.0 / max(frame_height, frame_width))
        analysis_width = max(2, int(round(frame_width * analysis_scale)))
        analysis_height = max(2, int(round(frame_height * analysis_scale)))
        analysis = cv2.resize(frame, (analysis_width, analysis_height), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(analysis, cv2.COLOR_BGR2GRAY)
        overall_sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharp_fallbacks.append({
            "frame": frame.copy(), "face": None, "time": frame_index / fps,
            "score": overall_sharpness, "eyes": False, "armInward": 999.0,
        })
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.08, minNeighbors=5,
            minSize=(max(40, analysis_width // 12), max(40, analysis_height // 12)),
        )
        if len(faces) == 0:
            continue
        center_x = analysis_width / 2
        face = max(
            faces,
            key=lambda box: float(box[2] * box[3]) - abs((box[0] + box[2] / 2) - center_x) * 4,
        )
        x, y, width_value, height_value = [int(value) for value in face]
        face_gray = gray[y:y + height_value, x:x + width_value]
        upper_face = face_gray[:max(1, int(round(height_value * 0.68))), :]
        detected_eyes = eye_cascade.detectMultiScale(
            upper_face, scaleFactor=1.06, minNeighbors=5,
            minSize=(max(10, width_value // 8), max(8, height_value // 10)),
        )
        eye_centers = [
            (eye_x + eye_width / 2, eye_y + eye_height / 2)
            for eye_x, eye_y, eye_width, eye_height in detected_eyes
            if eye_y + eye_height / 2 < height_value * 0.62
        ]
        open_eyes = any(
            abs(left[1] - right[1]) <= height_value * 0.18
            and abs(left[0] - right[0]) >= width_value * 0.20
            for eye_index, left in enumerate(eye_centers)
            for right in eye_centers[eye_index + 1:]
        )
        face_sharpness = float(cv2.Laplacian(face_gray, cv2.CV_64F).var())
        face_brightness = float(face_gray.mean())
        motion = 0.0
        if ok_previous and ok_next and previous is not None and following is not None:
            previous_small = cv2.resize(previous, (analysis_width, analysis_height), interpolation=cv2.INTER_AREA)
            following_small = cv2.resize(following, (analysis_width, analysis_height), interpolation=cv2.INTER_AREA)
            previous_gray = cv2.cvtColor(previous_small, cv2.COLOR_BGR2GRAY)
            following_gray = cv2.cvtColor(following_small, cv2.COLOR_BGR2GRAY)
            motion_region_start = min(analysis_height - 1, max(0, y + int(height_value * 0.65)))
            motion_region = cv2.absdiff(
                previous_gray[motion_region_start:, :], following_gray[motion_region_start:, :]
            )
            if motion_region.size:
                motion = float(motion_region.mean())
        brightness_penalty = max(0.0, 55.0 - face_brightness) + max(0.0, face_brightness - 210.0)
        arm_inward = cover_inward_arm_score(analysis, (x, y, width_value, height_value), cv2, np)
        score = (
            face_sharpness * 1.8 + overall_sharpness * 0.25
            - motion * 3.2 - brightness_penalty * 4 - arm_inward * 2400
        )
        if open_eyes:
            score += 5000
        inverse_scale = 1.0 / analysis_scale
        original_face = tuple(int(round(value * inverse_scale)) for value in (x, y, width_value, height_value))
        candidates.append({
            "frame": frame.copy(), "face": original_face,
            "time": frame_index / fps, "score": score, "eyes": open_eyes,
            "armInward": arm_inward,
        })
        if position_index % 6 == 0:
            update_job(kind, stage=f"正在筛选封面画面 {position_index}/{sample_count}", progress=99.6)
    capture.release()

    relaxed_open_eye_candidates = [
        item for item in candidates if item["eyes"] and float(item.get("armInward") or 0.0) <= 0.32
    ]
    open_eye_candidates = [item for item in candidates if item["eyes"]]
    relaxed_candidates = [
        item for item in candidates if float(item.get("armInward") or 0.0) <= 0.32
    ]
    pool = relaxed_open_eye_candidates or open_eye_candidates or relaxed_candidates or candidates or sharp_fallbacks
    if not pool:
        raise RuntimeError("数字人形象视频中没有可用于封面的画面。")
    pool.sort(key=lambda item: item["score"], reverse=True)
    # Randomize among the best frames so repeated videos do not always receive
    # the same cover, while keeping the focus/open-eye quality gate intact.
    best_group = pool[:min(4, len(pool))]
    selected = random.choice(best_group)
    return (
        selected["frame"], selected.get("face"), float(selected["time"]),
        bool(selected.get("eyes")), float(selected.get("armInward") or 0.0),
    )


def crop_cover_frame(frame: Any, face: tuple[int, int, int, int] | None) -> Any:
    frame_height, frame_width = frame.shape[:2]
    target_ratio = 3 / 4
    if frame_width / max(1, frame_height) <= target_ratio:
        crop_width = frame_width
        crop_height = min(frame_height, max(1, int(round(crop_width / target_ratio))))
    else:
        crop_height = frame_height
        crop_width = min(frame_width, max(1, int(round(crop_height * target_ratio))))
    if face is not None:
        face_x, face_y, face_width, face_height = face
        face_center_x = face_x + face_width / 2
        face_center_y = face_y + face_height / 2
    else:
        face_center_x = frame_width / 2
        face_center_y = crop_height * 0.30
    crop_x = int(round(face_center_x - crop_width / 2))
    crop_y = int(round(face_center_y - crop_height * 0.30))
    crop_x = max(0, min(frame_width - crop_width, crop_x))
    crop_y = max(0, min(frame_height - crop_height, crop_y))
    return frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]


def cover_font_path() -> Path:
    preferred = CUSTOM_FONT_DIR / "AlimamaDongFangDaKai-Regular.otf"
    if preferred.is_file():
        return preferred
    windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in ("msyhbd.ttc", "msyh.ttc", "simhei.ttf"):
        candidate = windows_fonts / name
        if candidate.is_file():
            return candidate
    raise RuntimeError("没有找到可用于封面的中文字体。")


def generate_video_cover(kind: str, avatar_path: Path, destination: Path,
                         title: str, top_color: str, bottom_color: str) -> Path:
    try:
        import cv2
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("封面图片组件没有安装。") from exc

    update_job(kind, stage="正在挑选封面画面", progress=99.6)
    frame, face, frame_time, eyes_confirmed, arm_inward = select_cover_frame(kind, avatar_path)
    cropped = crop_cover_frame(frame, face)
    rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    resampling = getattr(Image, "Resampling", Image).LANCZOS
    canvas = Image.fromarray(rgb).resize((1080, 1440), resampling)

    clean_title = normalize_video_title(title) or "未命名视频"
    lines = split_cover_title_lines(clean_title) or [clean_title]
    font_file = cover_font_path()
    max_text_width = 960
    selected_font = None
    line_boxes: list[tuple[int, int, int, int]] = []
    for font_size in range(96, 23, -2):
        font = ImageFont.truetype(str(font_file), font_size)
        measure = ImageDraw.Draw(canvas)
        boxes = [measure.textbbox((0, 0), line, font=font) for line in lines]
        if max(box[2] - box[0] for box in boxes) <= max_text_width:
            selected_font = font
            line_boxes = boxes
            break
    if selected_font is None:
        selected_font = ImageFont.truetype(str(font_file), 24)
        measure = ImageDraw.Draw(canvas)
        line_boxes = [measure.textbbox((0, 0), line, font=selected_font) for line in lines]

    line_heights = [box[3] - box[1] for box in line_boxes]
    line_spacing = max(16, int(round(getattr(selected_font, "size", 48) * 0.24)))
    text_height = sum(line_heights) + line_spacing * max(0, len(lines) - 1)
    vertical_padding = max(34, int(round(getattr(selected_font, "size", 48) * 0.48)))
    band_height = min(480, text_height + vertical_padding * 2)
    band_top = max(960, min(1440 - band_height, int(round(1090 - band_height / 2))))

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((0, band_top, 1080, band_top + band_height), fill=(0, 0, 0, 153))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(canvas)
    cursor_y = band_top + (band_height - text_height) / 2

    def rgb_color(value: str, fallback: str) -> tuple[int, int, int, int]:
        clean = normalize_hex_color(value, fallback).lstrip("#")
        return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16), 255

    colors = [rgb_color(top_color, "#FFFFFF"), rgb_color(bottom_color, "#FFE66D")]
    for index, (line, box, line_height) in enumerate(zip(lines, line_boxes, line_heights)):
        line_width = box[2] - box[0]
        draw.text(
            ((1080 - line_width) / 2 - box[0], cursor_y - box[1]), line,
            font=selected_font, fill=colors[min(index, len(colors) - 1)],
        )
        cursor_y += line_height + line_spacing

    temporary = TEMP_DIR / f"cover_{uuid.uuid4().hex}.jpg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        canvas.convert("RGB").save(temporary, format="JPEG", quality=95, subsampling=0)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    append_job_log(
        kind,
        f"封面已从数字人形象 {frame_time:.1f} 秒处随机选取；"
        f"清晰度、正脸和睁眼检测{'通过' if eyes_confirmed else '采用最佳可用画面'}；"
        f"动作舒展检测{'通过' if arm_inward <= 0.32 else '采用最自然候选'}；尺寸 1080x1440。",
    )
    return destination


def run_digital_human(kind: str, audio_path: Path, avatar_path: Path,
                      output_dir: Path, quality: str, resolution: str,
                      text_settings: dict[str, Any] | None = None) -> Path:
    module_name = "hdModule" if quality == "v2" else "humanModule"
    module_root = MODULES_ROOT / module_name
    python_exe = venv_python_exe(module_root / "venv")
    worker = APP_DIR / "model_worker.py"
    if not python_exe.exists() or not (module_root / "config.json").exists():
        raise RuntimeError(
            f"没有找到所选的数字人模块（{module_name}）。"
            "请在“组件与下载”中完成口型模型运行环境的安装。"
        )

    model_avatar, source_dimensions = prepare_avatar_for_model(kind, avatar_path, quality)

    request_dir = TEMP_DIR / uuid.uuid4().hex
    request_dir.mkdir(parents=True, exist_ok=True)
    model_output_dir = request_dir / "model_output"
    model_output_dir.mkdir(parents=True, exist_ok=True)
    request_path = request_dir / "request.json"
    request_path.write_text(json.dumps({
        "module_root": str(module_root),
        "ffmpeg_dir": str(FFMPEG_DIR),
        "audio_file": str(audio_path),
        "video_file": str(model_avatar),
        "watermark": False,
        "digital_auth": False,
        "output_dir": str(model_output_dir),
        "runtime": {
            "batch_size": MODEL_BATCH_SIZE,
            "parallel_face_detect": True,
            "parallel_threads": 4,
            "face_cache": False,
            "face_cache_dir": str((FACE_CACHE_DIR / module_name).resolve()),
        },
    }, ensure_ascii=False), encoding="utf-8")

    update_job(kind, stage="正在加载数字人模型", progress=52)
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    started = time.time()
    process = subprocess.Popen(
        [str(python_exe), str(worker), str(request_path)],
        cwd=str(module_root),
        env=module_environment(module_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=creation_flags,
    )
    result_value: Any = None
    worker_error: str | None = None
    model_started = started
    last_model_progress = 0.0
    v1_total_batches: int | None = None

    def report_model_progress(value: float) -> None:
        nonlocal last_model_progress
        value = max(last_model_progress, min(100.0, value))
        if value <= last_model_progress and value < 100:
            return
        last_model_progress = value
        elapsed = max(0.0, time.time() - model_started)
        eta = elapsed * (100 - value) / value if value >= 1 else 0
        detail = f"嘴型合成 {int(value)}% · 已用 {format_duration(elapsed)}"
        if eta > 0:
            detail += f" · 预计剩余 {format_duration(eta)}"
        mapped = 58 + value * 0.38
        update_job(kind, stage=detail, progress=min(96, round(mapped, 1)))

    assert process.stdout is not None
    for raw_line in process.stdout:
        if MAIN_CANCEL.is_set():
            kill_process_tree(process)
            raise TaskCancelled("任务已手动停止。")
        line = raw_line.strip()
        append_job_log(kind, line)
        if line.startswith("LOCALDH_RESULT="):
            try:
                result_value = json.loads(line.split("=", 1)[1])
            except Exception:
                result_value = line.split("=", 1)[1]
            report_model_progress(100)
            kill_process_tree(process)
            break
        elif line.startswith("LOCALDH_ERROR="):
            worker_error = line.split("=", 1)[1] or "数字人生成失败。"
            kill_process_tree(process)
            break
        elif line.startswith("LOCALDH_STAGE=READY"):
            model_started = time.time()
            update_job(kind, stage="嘴型合成 0% · 正在初始化", progress=58)

        queue_match = re.search(r"batch_size\s*:\s*(\d+)\s*,\s*len\s*:\s*(\d+)", line)
        if queue_match:
            batch_size = max(1, int(queue_match.group(1)))
            frame_count = max(1, int(queue_match.group(2)))
            v1_total_batches = (frame_count + batch_size - 1) // batch_size

        batch_match = re.search(r"\[Batch\s+(\d+)\]", line)
        if batch_match and v1_total_batches:
            report_model_progress(int(batch_match.group(1)) / v1_total_batches * 100)

        model_progress = parse_progress(line)
        if model_progress is not None:
            report_model_progress(model_progress)

    try:
        return_code = process.wait(timeout=5 if result_value is not None else 30)
    except subprocess.TimeoutExpired:
        kill_process_tree(process)
        try:
            return_code = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            return_code = -9
    if worker_error:
        if "VideoCapture" in worker_error or "cv2" in worker_error:
            raise RuntimeError("数字人模块读取形象视频失败。素材已自动转换为兼容格式，请重新生成；如果仍失败，请改用普通模式。")
        raise RuntimeError(worker_error)
    if return_code != 0 and result_value is None:
        tail = "\n".join(snapshot_job(kind).get("log", [])[-6:])
        raise RuntimeError(f"数字人生成失败。{tail[-500:]}")

    media_path = find_media_path(result_value) or newest_video(model_output_dir, started)
    if media_path is None:
        raise RuntimeError("数字人模块已运行完成，但没有找到生成的视频。")

    settings = text_settings or {}
    clean_title = normalize_video_title(settings.get("title"))
    destination = unique_output_path(
        output_dir,
        output_title_stem(clean_title, settings.get("text")),
        ".mp4",
    )
    result = export_resolution(
        kind, media_path, destination, resolution, source_dimensions, text_settings
    )
    cover_path = result.with_name(f"{result.stem}_封面.jpg")
    try:
        generate_video_cover(
            kind, avatar_path, cover_path,
            clean_title or output_title_stem("", settings.get("text")),
            str(settings.get("titleColorTop") or "#FFFFFF"),
            str(settings.get("titleColorBottom") or "#FFE66D"),
        )
    except Exception as exc:
        append_job_log(kind, f"封面生成未完成，视频已正常保留：{exc}")
    return result


def validate_payload(payload: dict[str, Any], preview: bool = False) -> dict[str, Any]:
    text = str(payload.get("text") or "").strip()
    voice_mode = str(payload.get("voiceMode") or "local")
    if not text and voice_mode != "upload":
        raise ValueError("请先输入文案。")
    speed = float(payload.get("speed") or 1.0)
    try:
        emotion_weight = float(payload.get("emotionWeight", 1.0))
    except (TypeError, ValueError):
        emotion_weight = 1.0
    try:
        cfg_value = float(payload.get("cfgValue", 2.0))
    except (TypeError, ValueError):
        cfg_value = 2.0
    try:
        inference_timesteps = int(float(payload.get("inferenceTimesteps", 10)))
    except (TypeError, ValueError):
        inference_timesteps = 10
    raw_music_volume = float(payload.get("musicVolume", 12) or 0)
    music_volume = raw_music_volume / 100 if raw_music_volume > 1 else raw_music_volume
    clean = {
        "text": text,
        "voiceMode": voice_mode,
        "speed": max(0.5, min(2.0, speed)),
        "emotionWeight": max(0.0, min(1.0, emotion_weight)),
        "emotionText": str(payload.get("emotionText") or "").strip()[:100],
        "cfgValue": max(1.0, min(5.0, cfg_value)),
        "inferenceTimesteps": max(4, min(30, inference_timesteps)),
        "promptText": str(payload.get("promptText") or "").strip(),
        "apiKey": str(payload.get("apiKey") or "").strip(),
        "voiceId": str(payload.get("voiceId") or "").strip(),
        "elevenVoiceRecordId": str(payload.get("elevenVoiceRecordId") or "").strip(),
        "elevenAccountId": str(payload.get("elevenAccountId") or "").strip(),
        "elevenGenerationMode": str(payload.get("elevenGenerationMode") or "").strip(),
        "elevenModelId": str(payload.get("elevenModelId") or "eleven_multilingual_v2").strip()[:100],
        "elevenOutputFormat": str(payload.get("elevenOutputFormat") or "mp3_44100_128"),
        "elevenSettings": normalize_elevenlabs_settings(payload.get("elevenSettings")),
        "localVoiceId": str(payload.get("localVoiceId") or "").strip(),
        "videoTitle": normalize_video_title(payload.get("videoTitle")),
        "titleColorTop": normalize_hex_color(payload.get("titleColorTop"), "#FFFFFF"),
        "titleColorBottom": normalize_hex_color(payload.get("titleColorBottom"), "#FFE66D"),
        "subtitleEnabled": bool(payload.get("subtitleEnabled", True)),
        "textFont": str(payload.get("textFont") or "dongfangdakai")
        if str(payload.get("textFont") or "dongfangdakai") in TEXT_FONTS else "dongfangdakai",
        "textShadow": str(payload.get("textShadow") or "standard")
        if str(payload.get("textShadow") or "standard") in TEXT_SHADOWS else "standard",
        "nameplateEnabled": bool(payload.get("nameplateEnabled", False)),
        "speakerName": normalize_speaker_name(payload.get("speakerName")),
        "speakerDetails": str(payload.get("speakerDetails") or "").strip()[:300],
        "brollEnabled": bool(payload.get("brollEnabled", False)),
        "musicId": str(payload.get("musicId") or "").strip(),
        "musicVolume": max(0.0, min(0.30, music_volume)),
        "customAudio": "",
    }
    if voice_mode == "upload" and not text:
        # 自己录音且没填文案：没有文字可对准，字幕与 B-roll 一并关闭
        clean["subtitleEnabled"] = False
        clean["brollEnabled"] = False
    if voice_mode == "local":
        voice_record = None
        if re.fullmatch(r"[a-f0-9]{32}", clean["localVoiceId"]):
            voice_record = next(
                (item for item in load_voice_records()
                 if item["id"] == clean["localVoiceId"] and item["provider"] == "local"),
                None,
            )
        if voice_record is not None:
            if voice_record.get("status") != "ready":
                raise ValueError("这个声音还没有克隆完成，请先完成声音克隆。")
            prompt_audio = VOICE_LIBRARY_DIR / voice_record["sample"]
            clean["promptText"] = voice_record.get("promptText") or ""
            clean["voiceEngine"] = str(voice_record.get("engine") or "v2")
        else:
            prompt_audio = Path(str(payload.get("promptAudio") or ""))
            clean["voiceEngine"] = "v2"
        if not prompt_audio.is_file():
            raise ValueError("请选择有效的参考声音。")
        clean["promptAudio"] = prompt_audio
    elif voice_mode == "upload":
        custom_audio = Path(str(payload.get("customAudio") or "").strip())
        try:
            custom_audio.resolve().relative_to(UPLOAD_DIR.resolve())
        except (ValueError, OSError):
            raise ValueError("录音文件无效，请重新上传。") from None
        if not custom_audio.is_file() or custom_audio.stat().st_size <= 44:
            raise ValueError("录音文件不存在或已被清理，请重新上传。")
        clean["customAudio"] = custom_audio
    else:
        cloud_record = None
        if re.fullmatch(r"[a-f0-9]{32}", clean["elevenVoiceRecordId"]):
            cloud_record = next(
                (item for item in load_voice_records()
                 if item["id"] == clean["elevenVoiceRecordId"]
                 and item["provider"] == "elevenlabs"),
                None,
            )
        if cloud_record is not None:
            clean["voiceId"] = clean["voiceId"] or str(cloud_record.get("voiceId") or "")
            clean["elevenAccountId"] = (
                clean["elevenAccountId"] or str(cloud_record.get("accountId") or "")
            )
            if not payload.get("elevenModelId"):
                clean["elevenModelId"] = str(
                    cloud_record.get("modelId") or "eleven_multilingual_v2"
                )
            if not payload.get("elevenOutputFormat"):
                clean["elevenOutputFormat"] = str(
                    cloud_record.get("outputFormat") or "mp3_44100_128"
                )
            if not isinstance(payload.get("elevenSettings"), dict):
                clean["elevenSettings"] = normalize_elevenlabs_settings(
                    cloud_record.get("settings")
                )
        if not clean["voiceId"]:
            raise ValueError("选择的 ElevenLabs 声音缺少 Voice ID，请先完成声音设置。")
        if clean["elevenOutputFormat"] not in ELEVENLABS_OUTPUT_FORMAT_IDS:
            clean["elevenOutputFormat"] = "mp3_44100_128"
        clean["elevenGenerationMode"] = normalize_elevenlabs_generation_mode(
            clean["elevenGenerationMode"], clean["elevenModelId"]
        )
        clean["elevenModelId"] = elevenlabs_model_for_mode(
            clean["elevenGenerationMode"], clean["elevenModelId"]
        )
        if not clean["apiKey"]:
            account, api_key = resolve_elevenlabs_account(
                clean["elevenAccountId"], clean["voiceId"]
            )
            clean["elevenAccountId"] = account["id"]
            clean["elevenAccountName"] = account["name"]
            clean["apiKey"] = api_key
        else:
            clean["elevenAccountName"] = "临时 API Key"

    if not preview:
        avatar = Path(str(payload.get("avatarVideo") or ""))
        if not avatar.is_file():
            raise ValueError("请选择有效的数字人素材视频。")
        avatar_person_id = ""
        payload_avatar_id = str(payload.get("avatarId") or "")
        if re.fullmatch(r"[a-f0-9]{32}", payload_avatar_id):
            avatar_record = next(
                (item for item in load_avatar_records() if item["id"] == payload_avatar_id),
                None,
            )
            if avatar_record is not None:
                avatar_person_id = str(avatar_record.get("personId") or "")
        clean["avatarPersonId"] = avatar_person_id
        output_dir = Path(str(payload.get("outputDir") or DEFAULT_OUTPUT))
        output_dir.mkdir(parents=True, exist_ok=True)
        free_bytes = shutil.disk_usage(output_dir).free
        if free_bytes < 5 * 1024 * 1024 * 1024:
            raise ValueError("保存磁盘剩余空间不足 5GB，请先清理空间或更换保存位置。")
        quality = "v1" if payload.get("quality") == "v1" else "v2"
        resolution = payload.get("resolution") if payload.get("resolution") in {"2k", "4k"} else "source"
        if quality == "v2" and resolution not in {"2k", "4k"}:
            resolution = "4k"
        music_path: Path | None = None
        music_name = ""
        if clean["musicId"]:
            music_record = next(
                (item for item in load_music_records() if item["id"] == clean["musicId"]),
                None,
            )
            if music_record is None:
                raise ValueError("选择的背景音乐已经不存在，请重新选择。")
            music_path = MUSIC_LIBRARY_DIR / music_record["file"]
            music_name = music_record["name"]
        clean.update({
            "avatarVideo": avatar,
            "outputDir": output_dir,
            "quality": quality,
            "resolution": resolution,
            "musicPath": music_path,
            "musicName": music_name,
        })
    return clean


def preview_task(payload: dict[str, Any]) -> None:
    try:
        data = validate_payload(payload, preview=True)
        if data["voiceMode"] == "upload":
            raise ValueError("自己录音模式不需要试听，直接生成即可。")
        preview_text = data["text"][:80]
        preview_dir = TEMP_DIR / "preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        if data["voiceMode"] == "local":
            output = preview_dir / f"preview_{uuid.uuid4().hex}.wav"
            audio = generate_local_voice(
                "preview", preview_text, data["promptAudio"], data["promptText"], output, data["speed"],
                engine=data.get("voiceEngine") or "v2",
                emotion_weight=data.get("emotionWeight", 1.0),
                emotion_text=data.get("emotionText") or "",
                cfg_value=data.get("cfgValue", 2.0),
                inference_timesteps=data.get("inferenceTimesteps", 10),
            )
            schedule_voice_stop(VOICE_LAST_USED)
        else:
            output = preview_dir / f"preview_{uuid.uuid4().hex}.mp3"
            generation_mode = normalize_elevenlabs_generation_mode(
                data.get("elevenGenerationMode"), data.get("elevenModelId")
            )
            if generation_mode == "v3_voice_match":
                update_job("preview", stage="V3 正在生成情感声音", progress=25)
                source = preview_dir / f"preview_{uuid.uuid4().hex}_v3.mp3"
                source_settings = dict(data["elevenSettings"])
                source_settings["stability"] = 0.50
                source_settings["similarityBoost"] = max(
                    0.85, float(source_settings.get("similarityBoost") or 0.75)
                )
                generate_elevenlabs_voice(
                    preview_text, data["apiKey"], data["voiceId"], source, data["speed"],
                    "eleven_v3", data["elevenOutputFormat"], source_settings,
                )
                record_elevenlabs_usage(
                    data.get("elevenAccountId") or "", len(preview_text)
                )
                update_job("preview", stage="正在转换回本人音色", progress=65)
                audio = convert_elevenlabs_voice(
                    data["apiKey"], data["voiceId"], source, output,
                    data["elevenOutputFormat"], data["elevenSettings"],
                )
                conversion_units = max(1, round(media_duration(source) * 1000 / 60))
                record_elevenlabs_usage(
                    data.get("elevenAccountId") or "", conversion_units
                )
            else:
                update_job("preview", stage="正在调用 ElevenLabs", progress=35)
                audio = generate_elevenlabs_voice(
                    preview_text, data["apiKey"], data["voiceId"], output, data["speed"],
                    data["elevenModelId"], data["elevenOutputFormat"], data["elevenSettings"],
                )
                record_elevenlabs_usage(
                    data.get("elevenAccountId") or "", len(preview_text)
                )
        update_job("preview", status="done", stage="试听已生成", progress=100, audio=str(audio), result=str(audio))
    except Exception as exc:
        update_job("preview", status="error", stage="试听失败", error=str(exc), message=str(exc))
        append_job_log("preview", traceback.format_exc())


def main_task(payload: dict[str, Any]) -> None:
    if not RUN_LOCK.acquire(blocking=False):
        update_job("main", status="error", stage="任务未开始", error="已有生成任务正在运行。")
        return
    try:
        data = validate_payload(payload, preview=False)
        output_dir: Path = data["outputDir"]
        update_job("main", outputDir=str(output_dir), stage="正在清理上次任务", progress=2)
        cleanup_stale_model_processes("main")
        cleanup_stale_voice_processes("main")
        # A warmed local voice model legitimately occupies about 4–5 GB.
        # The stricter free-memory check is applied after it is released.
        if data["voiceMode"] != "local":
            stop_local_voice()
            wait_for_gpu_memory("main")
        update_job("main", stage="正在准备", progress=3)
        raise_if_main_cancelled()
        audio_output = TEMP_DIR / f"voice_{uuid.uuid4().hex}.wav"
        audio = generate_segmented_script_audio(data, audio_output)
        raise_if_main_cancelled()
        update_job("main", audio=str(audio), stage="正在释放声音模型", progress=45)
        if data["voiceMode"] == "local":
            stop_local_voice()
            time.sleep(2)
        cleanup_stale_voice_processes("main")
        cleanup_stale_model_processes("main")
        broll_segments: list[dict[str, Any]] = []
        if data.get("brollEnabled"):
            try:
                broll_segments = plan_broll_segments(
                    "main",
                    data["text"],
                    media_duration(audio),
                    data.get("subtitleSegments") or [],
                    person_id=data.get("avatarPersonId") or "",
                    cues=data.get("subtitleCues") or None,
                )
            except TaskCancelled:
                raise
            except Exception as exc:
                append_job_log("main", f"智能素材匹配未完成，本次继续生成无素材版本：{exc}")
                update_job("main", stage="素材匹配未完成，继续生成数字人", progress=49)
        raise_if_main_cancelled()
        wait_for_gpu_memory("main")
        result = run_digital_human(
            "main", audio, data["avatarVideo"], output_dir, data["quality"], data["resolution"],
            {
                "title": data["videoTitle"],
                "subtitles": data["subtitleEnabled"],
                "font": data["textFont"],
                "shadow": data["textShadow"],
                "titleColorTop": data["titleColorTop"],
                "titleColorBottom": data["titleColorBottom"],
                "nameplate": data["nameplateEnabled"],
                "speakerName": data["speakerName"],
                "speakerDetails": data["speakerDetails"],
                "text": data["text"],
                "segments": data.get("subtitleSegments") or [],
                "cues": data.get("subtitleCues") or [],
                "musicPath": str(data["musicPath"]) if data.get("musicPath") else "",
                "musicVolume": data["musicVolume"],
                "brollSegments": broll_segments,
            },
        )
        cover_path = result.with_name(f"{result.stem}_封面.jpg")
        cover_ready = cover_path.is_file()
        update_job(
            "main", status="done",
            stage="视频和封面生成完成" if cover_ready else "视频生成完成",
            progress=100, result=str(result), cover=str(cover_path) if cover_ready else None,
            message="视频和封面已经生成。" if cover_ready else "视频已经生成，封面未能自动生成。",
        )
    except TaskCancelled as exc:
        update_job("main", status="error", stage="已手动停止", error=str(exc),
                   message="任务已手动停止，资源已释放。")
        append_job_log("main", "任务被手动停止。")
        stop_local_voice()
        cleanup_stale_voice_processes("main")
        cleanup_stale_model_processes("main")
    except Exception as exc:
        update_job("main", status="error", stage="生成失败", error=str(exc), message=str(exc))
        append_job_log("main", traceback.format_exc())
        stop_local_voice()
    finally:
        cleanup_stale_model_processes("main")
        RUN_LOCK.release()
        # 队列里还有等待任务时不预热声音模型：预热会立刻占 4-5GB 显存，
        # 导致下一条任务的显存检查失败（2026-08-16 连环失败根因）
        if not MAIN_CANCEL.is_set():
            with QUEUE_LOCK:
                has_pending = any(entry.get("status") == "pending" for entry in QUEUE_ITEMS)
            if not has_pending:
                schedule_voice_warmup(3)


def freeze_queue_voice_selection(
    candidate: dict[str, Any], validated: dict[str, Any]
) -> tuple[str, str]:
    """Freeze the exact voice and API account selected for one queue task."""
    voice_name = ""
    account_name = ""
    if validated["voiceMode"] == "upload":
        voice_name = "自己录音"
    elif validated["voiceMode"] == "local":
        voice_id = str(validated.get("localVoiceId") or "")
        voice = next(
            (item for item in load_voice_records() if item["id"] == voice_id), None
        )
        voice_name = str((voice or {}).get("name") or "本地声音")
    else:
        for key in (
            "voiceId", "elevenVoiceRecordId", "elevenAccountId", "elevenGenerationMode",
            "elevenModelId",
            "elevenOutputFormat", "elevenSettings",
        ):
            candidate[key] = validated.get(key)
        voice_record_id = str(validated.get("elevenVoiceRecordId") or "")
        voice = next(
            (item for item in load_voice_records() if item["id"] == voice_record_id), None
        )
        voice_name = str((voice or {}).get("name") or "ElevenLabs 声音")
        account_name = str(validated.get("elevenAccountName") or "ElevenLabs 账号")
    return voice_name, account_name


def stored_queue_payload(payload: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "text": text,
        "voiceMode": str(payload.get("voiceMode") or "local"),
        "localVoiceId": str(payload.get("localVoiceId") or ""),
        "promptAudio": str(payload.get("promptAudio") or ""),
        "promptText": str(payload.get("promptText") or ""),
        "requiresApiKey": (
            str(payload.get("voiceMode") or "local") == "elevenlabs"
            and bool(str(payload.get("apiKey") or "").strip())
        ),
        "voiceId": str(payload.get("voiceId") or ""),
        "elevenVoiceRecordId": str(payload.get("elevenVoiceRecordId") or ""),
        "elevenAccountId": str(payload.get("elevenAccountId") or ""),
        "elevenGenerationMode": normalize_elevenlabs_generation_mode(
            payload.get("elevenGenerationMode"), payload.get("elevenModelId")
        ),
        "elevenModelId": str(payload.get("elevenModelId") or "eleven_multilingual_v2"),
        "elevenOutputFormat": str(payload.get("elevenOutputFormat") or "mp3_44100_128"),
        "elevenSettings": normalize_elevenlabs_settings(payload.get("elevenSettings")),
        "speed": float(payload.get("speed") or 1.0),
        "emotionWeight": payload.get("emotionWeight", 1.0),
        "emotionText": str(payload.get("emotionText") or ""),
        "cfgValue": payload.get("cfgValue", 2.0),
        "inferenceTimesteps": payload.get("inferenceTimesteps", 10),
        "quality": "v1" if payload.get("quality") == "v1" else "v2",
        "resolution": str(payload.get("resolution") or "source"),
        "videoTitle": normalize_video_title(payload.get("videoTitle")),
        "titleColorTop": normalize_hex_color(payload.get("titleColorTop"), "#FFFFFF"),
        "titleColorBottom": normalize_hex_color(payload.get("titleColorBottom"), "#FFE66D"),
        "subtitleEnabled": bool(payload.get("subtitleEnabled", True)),
        "textFont": str(payload.get("textFont") or "dongfangdakai")
        if str(payload.get("textFont") or "dongfangdakai") in TEXT_FONTS else "dongfangdakai",
        "textShadow": str(payload.get("textShadow") or "standard")
        if str(payload.get("textShadow") or "standard") in TEXT_SHADOWS else "standard",
        "nameplateEnabled": bool(payload.get("nameplateEnabled", False)),
        "speakerName": normalize_speaker_name(payload.get("speakerName")),
        "speakerDetails": str(payload.get("speakerDetails") or "").strip()[:300],
        "brollEnabled": bool(payload.get("brollEnabled", False)),
        "musicId": str(payload.get("musicId") or ""),
        "musicVolume": float(payload.get("musicVolume", 12) or 0),
        "customAudio": str(payload.get("customAudio") or ""),
        "avatarId": str(payload.get("avatarId") or ""),
        "avatarVideo": str(payload.get("avatarVideo") or ""),
        "outputDir": str(payload.get("outputDir") or DEFAULT_OUTPUT),
    }


def runtime_queue_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload = dict(item.get("payload") or {})
    requires_api_key = bool(payload.pop("requiresApiKey", False))
    payload["apiKey"] = QUEUE_SECRETS.get(str(item.get("id") or ""), "")
    if requires_api_key and not payload["apiKey"]:
        raise RuntimeError("软件重启后不能恢复 ElevenLabs 密钥，请重新提交这批云端声音任务。")
    return payload


def create_task_queue(payload: dict[str, Any]) -> dict[str, Any]:
    global QUEUE_ITEMS, QUEUE_SECRETS, QUEUE_PAUSED
    raw_tasks = payload.get("tasks")
    if isinstance(raw_tasks, list):
        if len(raw_tasks) > 10:
            raise ValueError("一次最多提交 10 条文案。")
        filled = [
            (
                index + 1,
                normalize_video_title(item.get("title")),
                str(item.get("text") or "").strip(),
                str(item.get("musicId") or "").strip(),
                str(item.get("avatarId") or "").strip(),
            )
            for index, item in enumerate(raw_tasks[:10])
            if isinstance(item, dict) and str(item.get("text") or "").strip()
        ]
    else:
        raw_texts = payload.get("texts")
        if not isinstance(raw_texts, list):
            raise ValueError("批量文案格式无效。")
        if len(raw_texts) > 10:
            raise ValueError("一次最多提交 10 条文案。")
        filled = [
            (index + 1, "", str(value or "").strip(), "", "")
            for index, value in enumerate(raw_texts[:10])
            if str(value or "").strip()
        ]
    if not filled:
        raise ValueError("请至少输入一条批量文案。")
    if queue_is_busy() or snapshot_job("main")["status"] == "running":
        raise ValueError("已有批量任务正在运行。")
    if snapshot_job("clone")["status"] == "running":
        raise ValueError("请等待当前声音克隆完成。")

    items: list[dict[str, Any]] = []
    QUEUE_SECRETS = {}
    avatar_records = load_avatar_records()
    if not avatar_records:
        raise ValueError("请先上传至少一个数字人形象。")
    for task_order, (position, title, text, music_id, avatar_id) in enumerate(filled):
        candidate = dict(payload)
        candidate["text"] = text
        candidate["videoTitle"] = title
        candidate["musicId"] = music_id
        if avatar_id:
            avatar_record = next((item for item in avatar_records if item["id"] == avatar_id), None)
            if avatar_record is None:
                raise ValueError(f"任务 {position} 选择的数字人已经不存在。")
        else:
            avatar_record = avatar_records[task_order % len(avatar_records)]
        candidate["avatarId"] = avatar_record["id"]
        candidate["avatarVideo"] = str((AVATAR_DIR / avatar_record["video"]).resolve())
        validated = validate_payload(candidate, preview=False)
        voice_name, voice_account_name = freeze_queue_voice_selection(candidate, validated)
        item_id = uuid.uuid4().hex
        if (str(payload.get("voiceMode") or "local") == "elevenlabs"
                and bool(str(payload.get("apiKey") or "").strip())):
            QUEUE_SECRETS[item_id] = str(payload.get("apiKey") or "")
        items.append({
            "id": item_id,
            "position": position,
            "title": title or queue_title(text, position),
            "characters": len(text),
            "avatarId": avatar_record["id"],
            "avatarName": avatar_record["name"],
            "voiceName": voice_name,
            "voiceAccountName": voice_account_name,
            "status": "pending",
            "progress": 0,
            "stage": "等待生成",
            "result": None,
            "error": None,
            "createdAt": time.time(),
            "startedAt": None,
            "finishedAt": None,
            "payload": stored_queue_payload(candidate, text),
        })
    with QUEUE_LOCK:
        QUEUE_ITEMS = items
        QUEUE_PAUSED = False
        save_queue_state()
    QUEUE_WAKE.set()
    return queue_public_snapshot()


def append_task_to_queue(payload: dict[str, Any]) -> dict[str, Any]:
    """Append one immutable task snapshot while the current task keeps running."""
    global QUEUE_SECRETS, QUEUE_PAUSED
    text = str(payload.get("text") or "").strip()
    if not text and str(payload.get("voiceMode") or "local") != "upload":
        raise ValueError("请输入文案后再添加到队列。")
    if len(text) > 100000:
        raise ValueError("单条文案过长，请控制在 10 万字以内。")
    if snapshot_job("clone")["status"] == "running":
        raise ValueError("请等待当前声音克隆完成。")

    avatar_records = load_avatar_records()
    if not avatar_records:
        raise ValueError("请先上传至少一个数字人形象。")
    avatar_id = str(payload.get("avatarId") or "").strip()
    if avatar_id:
        avatar_record = next((item for item in avatar_records if item["id"] == avatar_id), None)
        if avatar_record is None:
            raise ValueError("选择的数字人已经不存在，请重新选择。")
    else:
        with QUEUE_LOCK:
            queued_count = len(QUEUE_ITEMS)
        avatar_record = avatar_records[queued_count % len(avatar_records)]

    candidate = dict(payload)
    candidate["text"] = text
    candidate["avatarId"] = avatar_record["id"]
    candidate["avatarVideo"] = str((AVATAR_DIR / avatar_record["video"]).resolve())
    validated = validate_payload(candidate, preview=False)
    voice_name, voice_account_name = freeze_queue_voice_selection(candidate, validated)

    item_id = uuid.uuid4().hex
    with QUEUE_LOCK:
        position = max((int(item.get("position") or 0) for item in QUEUE_ITEMS), default=0) + 1
        if (str(payload.get("voiceMode") or "local") == "elevenlabs"
                and bool(str(payload.get("apiKey") or "").strip())):
            QUEUE_SECRETS[item_id] = str(payload.get("apiKey") or "")
        title = normalize_video_title(payload.get("videoTitle"))
        if not title:
            title = queue_title(text, position) if text else (
                f"录音 {Path(str(payload.get('customAudio') or '')).stem or position}"
            )
        item = {
            "id": item_id,
            "position": position,
            "title": title,
            "characters": len(text),
            "avatarId": avatar_record["id"],
            "avatarName": avatar_record["name"],
            "voiceName": voice_name,
            "voiceAccountName": voice_account_name,
            "status": "pending",
            "progress": 0,
            "stage": "等待生成",
            "result": None,
            "error": None,
            "createdAt": time.time(),
            "startedAt": None,
            "finishedAt": None,
            "payload": stored_queue_payload(candidate, text),
        }
        QUEUE_ITEMS.append(item)
        # Adding from the workbench is an explicit request to generate. Do not leave
        # a newly added task silently trapped behind an old persisted global pause.
        QUEUE_PAUSED = False
        save_queue_state()
    QUEUE_WAKE.set()
    return {"ok": True, "taskId": item_id, "queue": queue_public_snapshot()}


def apply_queue_action(payload: dict[str, Any]) -> dict[str, Any]:
    """Maintain the queue and individual task holds without interrupting a running model process."""
    global QUEUE_PAUSED
    action = str(payload.get("action") or "").strip().lower()
    item_id = str(payload.get("id") or "").strip()
    with QUEUE_LOCK:
        item = next((entry for entry in QUEUE_ITEMS if entry.get("id") == item_id), None)
        if action == "pause":
            QUEUE_PAUSED = True
        elif action == "resume":
            QUEUE_PAUSED = False
        elif action == "clear_finished":
            removable = {"done", "error", "cancelled"}
            QUEUE_ITEMS[:] = [entry for entry in QUEUE_ITEMS if entry.get("status") not in removable]
        elif action in {
            "pause_item", "start_item", "delete", "cancel", "remove", "retry",
            "move_up", "move_down", "duplicate",
        }:
            if item is None:
                raise ValueError("没有找到这条队列任务。")
            status = str(item.get("status") or "pending")
            if action == "pause_item":
                if status == "running":
                    raise ValueError("这条任务正在生成。为保护当前成片，不能强制暂停模型；可暂停后续等待任务。")
                if status != "pending":
                    raise ValueError("只有等待中的任务可以暂停。")
                item.update({
                    "status": "paused", "stage": "单条任务已暂停", "error": None,
                })
            elif action == "start_item":
                if status == "running":
                    raise ValueError("这条任务已经在生成。")
                if status not in {"pending", "paused", "done", "error", "cancelled"}:
                    raise ValueError("这条任务当前不能开始。")
                if status != "pending":
                    item.update({
                        "status": "pending", "progress": 0, "stage": "等待优先生成",
                        "result": None, "error": None, "startedAt": None, "finishedAt": None,
                    })
                else:
                    item["stage"] = "等待优先生成"
                QUEUE_ITEMS.remove(item)
                first_pending = next(
                    (index for index, entry in enumerate(QUEUE_ITEMS) if entry.get("status") == "pending"),
                    None,
                )
                if first_pending is None:
                    last_running = max(
                        (index for index, entry in enumerate(QUEUE_ITEMS) if entry.get("status") == "running"),
                        default=-1,
                    )
                    first_pending = last_running + 1
                QUEUE_ITEMS.insert(first_pending, item)
                # Starting one task is also an explicit request to wake the worker.
                QUEUE_PAUSED = False
            elif action == "delete":
                if status == "running":
                    MAIN_CANCEL.set()
                    item["stage"] = "正在停止并删除…"
                QUEUE_ITEMS.remove(item)
                QUEUE_SECRETS.pop(item_id, None)
            elif action == "cancel":
                if status == "running":
                    MAIN_CANCEL.set()
                    item.update({
                        "stage": "正在停止…",
                        "message": "已请求停止：正在终止模型进程并释放显存。",
                    })
                elif status == "pending":
                    item.update({
                        "status": "cancelled", "progress": 100, "stage": "已取消",
                        "finishedAt": time.time(), "error": None,
                    })
            elif action == "remove":
                if status == "running":
                    MAIN_CANCEL.set()
                    item["stage"] = "正在停止并删除…"
                QUEUE_ITEMS.remove(item)
                QUEUE_SECRETS.pop(item_id, None)
            elif action == "retry":
                if status not in {"error", "cancelled", "paused"}:
                    raise ValueError("只有失败、已取消或已暂停的任务可以重试。")
                item.update({
                    "status": "pending", "progress": 0, "stage": "等待重新生成",
                    "result": None, "error": None, "startedAt": None, "finishedAt": None,
                })
            elif action in {"move_up", "move_down"}:
                if status != "pending":
                    raise ValueError("只能调整等待中任务的顺序。")
                pending_indices = [
                    index for index, entry in enumerate(QUEUE_ITEMS)
                    if entry.get("status") == "pending"
                ]
                current_index = QUEUE_ITEMS.index(item)
                pending_position = pending_indices.index(current_index)
                target_position = pending_position + (-1 if action == "move_up" else 1)
                if 0 <= target_position < len(pending_indices):
                    target_index = pending_indices[target_position]
                    QUEUE_ITEMS[current_index], QUEUE_ITEMS[target_index] = (
                        QUEUE_ITEMS[target_index], QUEUE_ITEMS[current_index]
                    )
            elif action == "duplicate":
                new_id = uuid.uuid4().hex
                new_item = json.loads(json.dumps(item, ensure_ascii=False))
                new_item.update({
                    "id": new_id,
                    "position": max(
                        (int(entry.get("position") or 0) for entry in QUEUE_ITEMS), default=0
                    ) + 1,
                    "status": "pending", "progress": 0, "stage": "等待生成",
                    "result": None, "error": None, "createdAt": time.time(),
                    "startedAt": None, "finishedAt": None,
                })
                QUEUE_ITEMS.append(new_item)
                if item_id in QUEUE_SECRETS:
                    QUEUE_SECRETS[new_id] = QUEUE_SECRETS[item_id]
        else:
            raise ValueError("不支持的队列操作。")
        save_queue_state()
    if not QUEUE_PAUSED and any(item.get("status") == "pending" for item in QUEUE_ITEMS):
        QUEUE_WAKE.set()
    return queue_public_snapshot()


def organize_queue_result(item: dict[str, Any], result: str | None) -> str | None:
    if not result:
        return None
    source = Path(result)
    if not source.is_file():
        return result
    # run_digital_human already names both the video and its cover from the
    # cleaned script title. Queue order remains visible in the workbench and
    # must not be prepended to the exported filename.
    return str(source)


def task_queue_worker() -> None:
    # worker 线程一旦崩溃，队列会假死（任务永远卡在 running、停止按钮无效），
    # 任何意外都必须记录日志并重启循环，绝不能让线程裸死
    while True:
        try:
            task_queue_worker_inner()
        except Exception:
            log_unhandled_exception("task-queue worker 异常退出，已自动重启")


def task_queue_worker_inner() -> None:
    while True:
        QUEUE_WAKE.wait()
        set_queue_awake(True)
        while True:
            with QUEUE_LOCK:
                if QUEUE_PAUSED:
                    QUEUE_WAKE.clear()
                    save_queue_state()
                    break
                item = next((entry for entry in QUEUE_ITEMS if entry.get("status") == "pending"), None)
                if item is None:
                    QUEUE_WAKE.clear()
                    save_queue_state()
                    break
                item["status"] = "running"
                item["stage"] = "正在准备"
                item["startedAt"] = time.time()
                item["error"] = None
                MAIN_CANCEL.clear()
                save_queue_state()

            reset_job("main")
            try:
                main_task(runtime_queue_payload(item))
            except TaskCancelled:
                pass
            except Exception as exc:
                update_job("main", status="error", stage="生成失败", error=str(exc), message=str(exc))
                append_job_log("main", traceback.format_exc())
            job = snapshot_job("main")
            result = None
            if job.get("status") == "done":
                try:
                    result = organize_queue_result(item, job.get("result"))
                    if result:
                        update_job("main", result=result)
                except Exception as exc:
                    append_job_log("main", f"整理批量任务文件名失败：{exc}")
                    result = job.get("result")
            with QUEUE_LOCK:
                if item in QUEUE_ITEMS:
                    if MAIN_CANCEL.is_set():
                        item["status"] = "cancelled"
                    else:
                        item["status"] = "done" if job.get("status") == "done" else "error"
                    item["progress"] = 100
                    if item["status"] == "done":
                        item["stage"] = "生成完成"
                    elif item["status"] == "cancelled":
                        item["stage"] = "已手动停止"
                    else:
                        item["stage"] = "生成失败"
                    item["result"] = result
                    item["cover"] = job.get("cover")
                    item["error"] = None if item["status"] == "done" else (job.get("error") or "任务已停止。")
                    item["finishedAt"] = time.time()
                    save_queue_state()
            # 任务结束后立即同步该平台账号的真实用量，修正本地估算账本（失败不影响队列继续）
            eleven_account_id = str((item.get("payload") or {}).get("elevenAccountId") or "")
            if eleven_account_id:
                try:
                    sync_elevenlabs_account(eleven_account_id)
                except Exception as exc:
                    append_job_log("main", f"任务结束后同步 ElevenLabs 用量失败：{exc}")
        set_queue_awake(False)


def initialize_task_queue() -> None:
    global QUEUE_WORKER
    load_queue_state()
    if QUEUE_WORKER is None or not QUEUE_WORKER.is_alive():
        QUEUE_WORKER = threading.Thread(target=task_queue_worker, daemon=True, name="task-queue")
        QUEUE_WORKER.start()
    if queue_is_busy() and not QUEUE_PAUSED:
        QUEUE_WAKE.set()


def gpu_status() -> dict[str, Any]:
    command = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "nvidia-smi.exe"
    if not command.exists():
        return {"available": False, "label": "未检测到 NVIDIA 显卡"}
    try:
        result = subprocess.run(
            [str(command), "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        parts = [part.strip() for part in result.stdout.strip().split(",")]
        if len(parts) >= 3:
            return {
                "available": True,
                "name": parts[0],
                "totalMb": int(parts[1]),
                "freeMb": int(parts[2]),
                "label": f"{parts[0]} · 就绪",
            }
    except Exception:
        pass
    return {"available": False, "label": "显卡状态未知"}


def component_status() -> dict[str, Any]:
    """各可选/必需组件的安装状态，供“组件与下载”页与前端降级用。"""
    hd_python = hd_venv_python()
    whisper_python = find_python_with_package("faster_whisper")
    return {
        "ffmpeg": FFMPEG_EXE.is_file(),
        "hdModule": (MODULES_ROOT / "hdModule" / "config.json").is_file(),
        "hdModuleVenv": hd_python.is_file(),
        "humanModule": (MODULES_ROOT / "humanModule" / "config.json").is_file(),
        "voiceV2Module": (MODULES_ROOT / "voiceV2Module" / "api.py").is_file(),
        "voxcpm": VOXCPM_PYTHON.is_file() and VOXCPM_MODEL_DIR.is_dir(),
        "whisperModel": WHISPER_MODEL_DIR.is_dir(),
        "whisperPython": whisper_python is not None,
        "brollMatcherModel": (BROLL_MODEL_DIR / "model.safetensors").is_file(),
        "brollClassifierModel": (BROLL_CLASSIFIER_MODEL_DIR / "pytorch_model.bin").is_file(),
        "gpuMinFreeMB": GPU_MIN_FREE_MB,
    }


# ---------------------------------------------------------------------------
# 首启安装向导：按需下载/安装组件（口型运行环境、字幕对齐模型、B-roll 模型）
# ---------------------------------------------------------------------------
SETUP_CANCEL = threading.Event()
SETUP_THREAD: threading.Thread | None = None

PYTHON310_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
PYTHON310_HOME = APP_DIR / "runtime" / "python310"
PYPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
TORCH_INDEX_URL = "https://download.pytorch.org/whl/cu128"
# torch wheel 直接走我们自己的断点续传下载器（pip 的断点续传在 Windows 上
# 下载大文件时容易中断重来/Unpack 撞文件锁，2026-08-17 实测踩过）
TORCH_WHEEL_URL = (
    "https://download.pytorch.org/whl/cu128/"
    "torch-2.8.0%2Bcu128-cp310-cp310-win_amd64.whl"
)
TORCH_WHEEL_NAME = "torch-2.8.0+cu128-cp310-cp310-win_amd64.whl"
INSIGHTFACE_WHEEL_URL = (
    "https://github.com/Gourieff/Assets/raw/main/Insightface/"
    "insightface-0.7.3-cp310-cp310-win_amd64.whl"
)

# ModelScope 文件直链（resolve/master 支持 Range 断点续传，2026-08-17 实测返回 206）
MODELSCOPE_FILE_URL = "https://modelscope.cn/models/{repo}/resolve/master/{path}"
WHISPER_DOWNLOAD_DIR = DATA_DIR / "models" / "faster-whisper-large-v3-turbo"
MODEL_DOWNLOADS: dict[str, tuple[str, Path, list[str]]] = {
    "whisper": (
        "pengzhendong/faster-whisper-large-v3-turbo",
        WHISPER_DOWNLOAD_DIR,
        ["config.json", "model.bin", "tokenizer.json", "vocabulary.json",
         "preprocessor_config.json"],
    ),
    "bge": (
        "AI-ModelScope/bge-small-zh-v1.5",
        BROLL_MODEL_DIR,
        ["config.json", "config_sentence_transformers.json", "model.safetensors",
         "modules.json", "sentence_bert_config.json", "special_tokens_map.json",
         "tokenizer.json", "tokenizer_config.json", "vocab.txt", "1_Pooling/config.json"],
    ),
    "clip": (
        "openai-mirror/clip-vit-base-patch32",
        BROLL_CLASSIFIER_MODEL_DIR,
        ["config.json", "merges.txt", "preprocessor_config.json", "pytorch_model.bin",
         "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json", "vocab.json"],
    ),
}

SETUP_STEP_META: dict[str, dict[str, Any]] = {
    "pythonEnv": {
        "name": "口型模型运行环境",
        "description": "Python 3.10 + PyTorch（CUDA 版）+ 口型模型依赖。没有它无法生成数字人画面，必装。",
        "sizeHint": "下载约 3.5GB",
        "required": True,
    },
    "whisperModel": {
        "name": "字幕逐字对齐模型",
        "description": "faster-whisper large-v3-turbo。不装也能出片，但字幕与 B-roll 的时间轴会明显不准，推荐安装。",
        "sizeHint": "下载约 1.7GB",
        "required": False,
    },
    "brollModels": {
        "name": "B-roll 智能匹配模型",
        "description": "文案理解 + 画面分类模型。只在使用 B-roll 智能插入画面时需要，不用可以不装。",
        "sizeHint": "下载约 0.7GB",
        "required": False,
    },
}
SETUP_STEP_WEIGHTS = {"pythonEnv": 60, "whisperModel": 25, "brollModels": 15}

# 离线组件包（2026-08-17）：把大体积下载项（torch/insightface/Python 安装器/
# whisper/bge/clip 模型）提前打成「组件离线包」随安装器一起分发，安装向导
# 识别到后直接用本地文件，不再联网下载。目录约定：
#   组件离线包/python/python-3.10.11-amd64.exe
#   组件离线包/wheels/*.whl（torch / torchvision / torchaudio / insightface）
#   组件离线包/models/<模型目录名>/<文件>（目录名与 MODEL_DOWNLOADS 目标目录一致）
# 解析顺序：环境变量 LOCAL_DH_SETUP_BUNDLE > local-config.json 的
# setupBundleDir > 自动探测安装目录内/旁的「组件离线包」文件夹。
def setup_bundle_dir() -> Path | None:
    configured = config_path("setupBundleDir", "LOCAL_DH_SETUP_BUNDLE")
    if configured and configured.is_dir():
        return configured
    for candidate in (APP_DIR / "组件离线包", APP_DIR.parent / "组件离线包"):
        if candidate.is_dir():
            return candidate
    return configured  # 配置过但目录不存在时也返回，供界面提示"路径无效"


def bundle_file(*parts: str) -> Path | None:
    bundle = setup_bundle_dir()
    if bundle is None:
        return None
    candidate = bundle.joinpath(*parts)
    return candidate if candidate.is_file() else None


def bundle_glob(subdir: str, pattern: str) -> Path | None:
    bundle = setup_bundle_dir()
    if bundle is None:
        return None
    matches = sorted((bundle / subdir).glob(pattern))
    return matches[0] if matches else None


def bundle_snapshot() -> dict[str, Any]:
    bundle = setup_bundle_dir()
    items = {
        "pythonInstaller": bundle_file("python", "python-3.10.11-amd64.exe") is not None,
        "torch": bundle_file("wheels", TORCH_WHEEL_NAME) is not None,
        "torchvisionAudio": (
            bundle_glob("wheels", "torchvision-0.23.0*.whl") is not None
            and bundle_glob("wheels", "torchaudio-2.8.0*.whl") is not None
        ),
        "insightface": bundle_file("wheels", "insightface-0.7.3-cp310-cp310-win_amd64.whl") is not None,
    }
    for key, (_, target_dir, names) in MODEL_DOWNLOADS.items():
        items[key] = (
            bundle is not None
            and all((bundle / "models" / target_dir.name / name).is_file() for name in names)
        )
    available = bundle is not None and bundle.is_dir() and any(items.values())
    return {
        "path": str(bundle) if bundle else "",
        "available": bool(available),
        "items": items,
    }


def venv_python_exe(venv_dir: Path) -> Path:
    """conda 风格环境 python.exe 在根目录；标准 venv 在 Scripts 下。两种布局都兼容。"""
    root_exe = venv_dir / "python.exe"
    if root_exe.is_file():
        return root_exe
    return venv_dir / "Scripts" / "python.exe"


def hd_venv_dir() -> Path:
    return MODULES_ROOT / "hdModule" / "venv"


def hd_venv_python() -> Path:
    return venv_python_exe(hd_venv_dir())


def setup_running() -> bool:
    thread = SETUP_THREAD
    return thread is not None and thread.is_alive()


def setup_step_installed(step_id: str) -> bool:
    if step_id == "pythonEnv":
        python_exe = hd_venv_python()
        return (
            python_exe.is_file()
            and python_has_package(python_exe, "torch")
            and python_has_package(python_exe, "torchvision")
            and python_has_package(python_exe, "onnxruntime")
        )
    if step_id == "whisperModel":
        model_ok = (WHISPER_DOWNLOAD_DIR / "model.bin").is_file() or (
            WHISPER_MODEL_DIR.is_dir() and (WHISPER_MODEL_DIR / "model.bin").is_file()
        )
        return model_ok and find_python_with_package("faster_whisper") is not None
    if step_id == "brollModels":
        return (
            (BROLL_MODEL_DIR / "model.safetensors").is_file()
            and (BROLL_CLASSIFIER_MODEL_DIR / "pytorch_model.bin").is_file()
        )
    return False


def download_with_resume(url: str, destination: Path,
                         progress=None, cancel: threading.Event | None = None,
                         max_retries: int = 8) -> None:
    """带断点续传的文件下载：先下 .part，完成后改名；连接中断自动从断点重试。"""
    part_path = destination.with_name(destination.name + ".part")
    destination.parent.mkdir(parents=True, exist_ok=True)
    attempt = 0
    while True:
        downloaded = part_path.stat().st_size if part_path.exists() else 0
        try:
            request = urllib.request.Request(url)
            if downloaded:
                request.add_header("Range", f"bytes={downloaded}-")
            with urllib.request.urlopen(request, timeout=60) as response:
                if downloaded and response.status == 200:
                    downloaded = 0  # 服务器忽略了 Range，重新下载
                    part_path.unlink(missing_ok=True)
                total = downloaded + int(response.headers.get("Content-Length") or 0)
                with part_path.open("ab" if downloaded else "wb") as handle:
                    while True:
                        if cancel is not None and cancel.is_set():
                            raise TaskCancelled("安装已手动取消。")
                        chunk = response.read(1 << 20)
                        if not chunk:
                            break
                        handle.write(chunk)
                        downloaded += len(chunk)
                        if progress:
                            progress(downloaded, total)
            # 完整性校验：连接被静默截断时 read 可能返回 EOF 而不报错（实测踩过），
            # 尺寸不足按异常处理走进度保留的重试（.part 续传）。
            if total and part_path.stat().st_size < total:
                raise IOError(f"下载不完整（{part_path.stat().st_size}/{total} 字节）")
            break
        except TaskCancelled:
            raise
        except Exception:
            attempt += 1
            if attempt > max_retries:
                raise
            time.sleep(min(30, 2 * attempt))
    part_path.replace(destination)


def run_setup_command(command: list[str], log_name: str, timeout: int = 7200,
                      progress=None) -> None:
    """跑安装命令，输出写日志文件（避免管道缓冲区堵死子进程），支持取消。

    progress(fraction, label) 可选：轮询时从日志尾部解析 "x.x GB/y.y GB"
    形式的下载进度回传（pip 下载大 wheel 时用）。
    """
    append_job_log("setup", "执行：" + " ".join(str(part) for part in command)[:180])
    log_path = LOG_DIR / f"{log_name}.log"
    with open(log_path, "a", encoding="utf-8", errors="replace") as log_file:
        process = subprocess.Popen(
            [str(part) for part in command],
            stdout=log_file, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        deadline = time.time() + timeout
        while process.poll() is None:
            if SETUP_CANCEL.is_set():
                kill_process_tree(process)
                raise TaskCancelled("安装已手动取消。")
            if time.time() > deadline:
                kill_process_tree(process)
                raise TimeoutError(f"安装步骤超时（{log_name}）。")
            if progress:
                try:
                    with open(log_path, "rb") as reader:
                        reader.seek(0, 2)
                        size = reader.tell()
                        reader.seek(max(0, size - 4096))
                        tail = reader.read().decode("utf-8", errors="replace")
                    matches = re.findall(r"([\d.]+)\s*(GB|MB)\s*/\s*([\d.]+)\s*(GB|MB)", tail)
                    if matches:
                        done, done_unit, total, total_unit = matches[-1]
                        done_mb = float(done) * (1024 if done_unit == "GB" else 1)
                        total_mb = float(total) * (1024 if total_unit == "GB" else 1)
                        if total_mb > 0:
                            progress(min(1.0, done_mb / total_mb), f"{done}{done_unit}/{total}{total_unit}")
                except Exception:
                    pass
            time.sleep(1)
    if process.returncode != 0:
        raise RuntimeError(f"安装命令执行失败（详见 logs/{log_name}.log）。")


def find_python310() -> Path | None:
    candidate = PYTHON310_HOME / "python.exe"
    if candidate.is_file():
        return candidate
    launcher = shutil.which("py")
    if launcher:
        try:
            completed = subprocess.run(
                [launcher, "-3.10", "-c", "import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=30,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            found = Path(completed.stdout.strip())
            if completed.returncode == 0 and found.is_file():
                return found
        except Exception:
            pass
    return None


def setup_step_python_env(progress_base: float, progress_span: float) -> None:
    python_exe = hd_venv_python()
    if (
        python_exe.is_file()
        and python_has_package(python_exe, "torch")
        and python_has_package(python_exe, "onnxruntime")
    ):
        append_job_log("setup", "口型模型运行环境已就绪，跳过。")
        return
    if not (MODULES_ROOT / "hdModule" / "config.json").is_file():
        raise RuntimeError("口型模型文件（hdModule）不在安装目录里，安装包可能不完整。")

    base_python = find_python310()
    if base_python is None:
        installer = bundle_file("python", "python-3.10.11-amd64.exe")
        from_bundle = installer is not None
        if from_bundle:
            update_job("setup", stage="正在安装 Python 3.10（离线组件包）")
        else:
            update_job("setup", stage="正在下载 Python 3.10 安装器")
            installer = TEMP_DIR / "python-3.10.11-amd64.exe"
            download_with_resume(
                PYTHON310_URL, installer,
                progress=lambda done, total: update_job(
                    "setup", progress=int(progress_base + progress_span * 0.05 * (done / max(1, total)))),
                cancel=SETUP_CANCEL,
            )
            update_job("setup", stage="正在安装 Python 3.10（静默安装，约 1 分钟）")
        run_setup_command(
            [str(installer), "/quiet", "InstallAllUsers=0",
             f"TargetDir={PYTHON310_HOME}", "PrependPath=0", "Include_test=0",
             "Include_launcher=0", "AssociateFiles=0", "Shortcuts=0"],
            "setup-python-install", timeout=1800,
        )
        if not from_bundle:
            installer.unlink(missing_ok=True)
        base_python = PYTHON310_HOME / "python.exe"
        if not base_python.is_file():
            raise RuntimeError("Python 3.10 安装失败，请查看 logs/setup-python-install.log。")
    update_job("setup", progress=int(progress_base + progress_span * 0.05))

    if not python_exe.is_file():
        update_job("setup", stage="正在创建口型模型虚拟环境")
        run_setup_command([str(base_python), "-m", "venv", str(hd_venv_dir())],
                          "setup-venv", timeout=900)
        if not python_exe.is_file():
            raise RuntimeError("虚拟环境创建失败，请查看 logs/setup-venv.log。")
    # VC++ 运行库 DLL 随包内置（runtime/vcredist）：目标机不用装系统级 redist，
    # 旧版/损坏的 redist 也不会冲突——DLL 放在 venv 的 python.exe 旁边即被优先加载。
    vcredist_dir = APP_DIR / "runtime" / "vcredist"
    if vcredist_dir.is_dir():
        for dll in vcredist_dir.glob("*.dll"):
            shutil.copy2(dll, python_exe.parent / dll.name)
    update_job("setup", progress=int(progress_base + progress_span * 0.1))

    run_setup_command(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "-i", PYPI_MIRROR],
        "setup-pip-upgrade", timeout=900,
    )
    if not python_has_package(python_exe, "torch"):
        wheel_path = bundle_file("wheels", TORCH_WHEEL_NAME)
        from_bundle = wheel_path is not None
        if not from_bundle:
            update_job("setup", stage="正在下载 PyTorch CUDA 版（约 3.5GB，支持断点续传）")
            wheel_path = TEMP_DIR / TORCH_WHEEL_NAME
            download_with_resume(
                TORCH_WHEEL_URL, wheel_path,
                progress=lambda done, total: update_job(
                    "setup",
                    progress=int(progress_base + progress_span * (0.1 + 0.55 * (done / max(1, total)))),
                    stage=(f"正在下载 PyTorch CUDA 版"
                           f"（{done / 1024 ** 3:.1f}/{total / 1024 ** 3:.1f} GB）"),
                ),
                cancel=SETUP_CANCEL,
            )
        else:
            update_job("setup", stage="正在安装 PyTorch（离线组件包）")
        update_job("setup", progress=int(progress_base + progress_span * 0.65),
                   stage="正在安装 PyTorch（本地安装包）")
        try:
            run_setup_command(
                [str(python_exe), "-m", "pip", "install", str(wheel_path), "-i", PYPI_MIRROR],
                "setup-pip-torch", timeout=7200,
            )
        finally:
            if not from_bundle:
                wheel_path.unlink(missing_ok=True)
    if not python_has_package(python_exe, "torchvision"):
        # requirements.txt 漏了 torchvision/torchaudio（原 conda 环境里有）。
        # 离线组件包里有两个 whl 就直接本地装，否则走 pytorch 官方 index
        tv_wheel = bundle_glob("wheels", "torchvision-0.23.0*.whl")
        ta_wheel = bundle_glob("wheels", "torchaudio-2.8.0*.whl")
        if tv_wheel is not None and ta_wheel is not None:
            update_job("setup", stage="正在安装 torchvision/torchaudio（离线组件包）")
            run_setup_command(
                [str(python_exe), "-m", "pip", "install",
                 str(tv_wheel), str(ta_wheel), "-i", PYPI_MIRROR],
                "setup-pip-torchvision", timeout=1800,
            )
        else:
            run_setup_command(
                [str(python_exe), "-m", "pip", "install",
                 "torchvision==0.23.0", "torchaudio==2.8.0",
                 "--index-url", TORCH_INDEX_URL],
                "setup-pip-torchvision", timeout=1800,
            )
    update_job("setup", progress=int(progress_base + progress_span * 0.7))

    if not python_has_package(python_exe, "insightface"):
        # insightface 没有官方 Windows wheel，源码编译需要 MSVC Build Tools；
        # 用社区预编译 wheel（Gourieff/Assets，ComfyUI 社区通用来源）。
        # 离线组件包里带了就直接本地装（GitHub 在国内不稳，优先离线）。
        face_wheel = bundle_file("wheels", "insightface-0.7.3-cp310-cp310-win_amd64.whl")
        from_bundle = face_wheel is not None
        if not from_bundle:
            update_job("setup", stage="正在下载 insightface 人脸识别组件（约 260MB）")
            face_wheel = TEMP_DIR / "insightface-0.7.3-cp310-cp310-win_amd64.whl"
        try:
            if not from_bundle:
                download_with_resume(
                    INSIGHTFACE_WHEEL_URL, face_wheel,
                    progress=lambda done, total: update_job(
                        "setup",
                        progress=int(progress_base + progress_span * (0.7 + 0.1 * (done / max(1, total)))),
                        stage=(f"正在下载 insightface 人脸识别组件"
                               f"（{done / 1024 ** 2:.0f}/{total / 1024 ** 2:.0f} MB）"),
                    ),
                    cancel=SETUP_CANCEL,
                )
            else:
                update_job("setup", stage="正在安装 insightface 人脸识别组件（离线组件包）")
            run_setup_command(
                [str(python_exe), "-m", "pip", "install", str(face_wheel), "-i", PYPI_MIRROR],
                "setup-pip-insightface", timeout=3600,
            )
        finally:
            if not from_bundle:
                face_wheel.unlink(missing_ok=True)
    update_job("setup", progress=int(progress_base + progress_span * 0.8),
               stage="正在安装口型模型依赖")
    requirements = MODULES_ROOT / "hdModule" / "requirements.txt"
    if requirements.is_file():
        run_setup_command(
            [str(python_exe), "-m", "pip", "install", "-r", str(requirements), "-i", PYPI_MIRROR],
            "setup-pip-requirements", timeout=7200,
        )
    _PYTHON_PACKAGE_CACHE.clear()
    if not (
        python_has_package(python_exe, "torch")
        and python_has_package(python_exe, "torchvision")
        and python_has_package(python_exe, "onnxruntime")
    ):
        raise RuntimeError("运行环境校验失败（torch/torchvision/onnxruntime 导入异常），请查看 logs 下的 setup-pip 日志。")


def setup_download_models(keys: list[str], progress_base: float, progress_span: float) -> None:
    files: list[tuple[str, Path, str, str]] = []
    for key in keys:
        repo, target_dir, names = MODEL_DOWNLOADS[key]
        for name in names:
            if not (target_dir / name).is_file():
                files.append((MODELSCOPE_FILE_URL.format(repo=repo, path=name),
                              target_dir / name, target_dir.name, name))
    if not files:
        return
    completed = 0
    for url, destination, model_dir_name, rel_name in files:
        base = progress_base + progress_span * completed / len(files)
        span = progress_span / len(files)
        # 离线组件包优先：models/<模型目录名>/<相对路径> 存在则直接拷贝（rel_name
        # 可能是 "1_Pooling/config.json" 这类嵌套路径），否则走 ModelScope 下载。
        source = bundle_file("models", model_dir_name, rel_name)
        if source is not None:
            update_job("setup", stage=f"正在从离线组件包复制 {destination.name}（{completed + 1}/{len(files)}）")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            completed += 1
            update_job("setup", progress=min(99, int(base + span)))
            continue
        update_job("setup", stage=f"正在下载 {destination.name}（{completed + 1}/{len(files)}）")
        download_with_resume(
            url, destination,
            progress=lambda done, total, b=base, s=span: update_job(
                "setup", progress=min(99, int(b + s * (done / max(1, total))))),
            cancel=SETUP_CANCEL,
        )
        completed += 1


def setup_step_whisper(progress_base: float, progress_span: float) -> None:
    python_exe = hd_venv_python()
    if not python_exe.is_file():
        raise RuntimeError("需要先安装“口型模型运行环境”，字幕对齐模型要装到它的 Python 里。")
    if not python_has_package(python_exe, "faster_whisper"):
        update_job("setup", stage="正在安装 faster-whisper 组件")
        run_setup_command(
            [str(python_exe), "-m", "pip", "install", "faster-whisper", "-i", PYPI_MIRROR],
            "setup-pip-whisper", timeout=3600,
        )
        _PYTHON_PACKAGE_CACHE.clear()
    update_job("setup", progress=int(progress_base + progress_span * 0.15))
    setup_download_models(["whisper"], progress_base + progress_span * 0.15, progress_span * 0.85)
    if not (WHISPER_DOWNLOAD_DIR / "model.bin").is_file():
        raise RuntimeError("字幕对齐模型下载不完整，请重试。")


def setup_step_broll(progress_base: float, progress_span: float) -> None:
    setup_download_models(["bge", "clip"], progress_base, progress_span)
    if not setup_step_installed("brollModels"):
        raise RuntimeError("B-roll 模型下载不完整，请重试。")


def setup_runner(steps: list[str]) -> None:
    total_weight = sum(SETUP_STEP_WEIGHTS.get(step, 10) for step in steps) or 1
    cursor = 0.0
    try:
        for step in steps:
            if SETUP_CANCEL.is_set():
                raise TaskCancelled("安装已手动取消。")
            meta = SETUP_STEP_META[step]
            span = 100.0 * SETUP_STEP_WEIGHTS.get(step, 10) / total_weight
            update_job("setup", stage=f"正在安装：{meta['name']}", progress=int(cursor))
            append_job_log("setup", f"开始安装 {meta['name']}")
            if step == "pythonEnv":
                setup_step_python_env(cursor, span)
            elif step == "whisperModel":
                setup_step_whisper(cursor, span)
            elif step == "brollModels":
                setup_step_broll(cursor, span)
            cursor += span
        _PYTHON_PACKAGE_CACHE.clear()
        update_job("setup", status="done", stage="全部安装完成", progress=100,
                   finishedAt=time.time())
        append_job_log("setup", "全部组件安装完成。")
    except TaskCancelled as exc:
        update_job("setup", status="cancelled", stage="已取消", error=str(exc),
                   finishedAt=time.time())
    except Exception as exc:  # noqa: BLE001 - 向导要把任何失败原样展示
        append_job_log("setup", f"安装失败：{exc}")
        update_job("setup", status="error", stage="安装失败", error=str(exc)[:300],
                   finishedAt=time.time())


def start_setup(steps: list[str]) -> None:
    global SETUP_THREAD
    invalid = [step for step in steps if step not in SETUP_STEP_META]
    if invalid:
        raise ValueError("未知的安装项。")
    if not steps:
        raise ValueError("请选择要安装的组件。")
    if setup_running():
        raise RuntimeError("已有安装任务在进行中。")
    if "whisperModel" in steps and "pythonEnv" not in steps and not hd_venv_python().is_file():
        raise RuntimeError("字幕对齐模型依赖口型模型运行环境，请勾选“口型模型运行环境”一起安装。")
    reset_job("setup")
    SETUP_CANCEL.clear()
    SETUP_THREAD = threading.Thread(target=setup_runner, args=(steps,), daemon=True)
    SETUP_THREAD.start()


def pick_path(kind: str) -> dict[str, Any]:
    if kind == "folder" and FOLDER_PICKER_SCRIPT.is_file():
        powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        completed = subprocess.run(
            [
                str(powershell), "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass",
                "-File", str(FOLDER_PICKER_SCRIPT), "-InitialPath", str(DEFAULT_OUTPUT),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode != 0:
            raise RuntimeError("文件夹选择窗口打开失败，请在路径框中直接输入保存位置。")
        selected = completed.stdout.strip().lstrip("\ufeff")
        return {"cancelled": not bool(selected), "path": selected} if selected else {"cancelled": True}

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    try:
        if kind == "folder":
            selected = filedialog.askdirectory(parent=root, initialdir=str(DEFAULT_OUTPUT), title="选择保存位置")
        else:
            filters = {
                "audio": [("音频文件", "*.wav *.mp3 *.m4a *.flac *.aac"), ("所有文件", "*.*")],
                "voice": [("音频或视频", "*.wav *.mp3 *.m4a *.flac *.aac *.mp4 *.mov *.avi *.mkv"), ("所有文件", "*.*")],
                "video": [("视频文件", "*.mp4 *.mov *.avi *.mkv"), ("所有文件", "*.*")],
                "text": [("文本文件", "*.txt *.md"), ("所有文件", "*.*")],
            }
            selected = filedialog.askopenfilename(parent=root, title="选择文件", filetypes=filters.get(kind, [("所有文件", "*.*")]))
    finally:
        root.destroy()
    if not selected:
        return {"cancelled": True}
    response: dict[str, Any] = {"cancelled": False, "path": selected}
    if kind == "text":
        raw = Path(selected).read_bytes()
        for encoding in ("utf-8-sig", "gb18030", "utf-16"):
            try:
                response["content"] = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        response.setdefault("content", raw.decode("utf-8", errors="replace"))
    return response


def validate_output_folder(value: Any) -> Path:
    raw = os.path.expandvars(str(value or "").strip().strip('"'))
    if not raw:
        raise ValueError("请输入或选择视频保存文件夹。")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise ValueError("请输入完整的文件夹路径，例如 D:\\数字人视频。")
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise ValueError("这个位置不是有效文件夹。")
    try:
        probe = path / f".local-dh-write-test-{uuid.uuid4().hex}.tmp"
        probe.write_bytes(b"")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        raise ValueError(f"这个文件夹无法写入：{exc}") from exc
    return path.resolve()


def open_output_folder(target: Any) -> Path:
    """Open a known output location with Explorer without relying on os.startfile."""
    path = Path(str(target or DEFAULT_OUTPUT)).expanduser()
    if path.is_file():
        path = path.parent
    if not path.exists():
        path = DEFAULT_OUTPUT
    path = validate_output_folder(path)
    explorer = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "explorer.exe"
    if not explorer.is_file():
        raise RuntimeError("没有找到 Windows 文件资源管理器。")
    creation_flags = (
        getattr(subprocess, "DETACHED_PROCESS", 0)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    )
    subprocess.Popen(
        [str(explorer), str(path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=creation_flags,
    )
    return path


def load_broll_catalog() -> dict[str, Any]:
    with BROLL_LOCK:
        if not BROLL_INDEX.is_file():
            return {"catalogVersion": 1, "assets": []}
        try:
            payload = json.loads(BROLL_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return {"catalogVersion": 1, "assets": []}
        if not isinstance(payload, dict) or not isinstance(payload.get("assets"), list):
            return {"catalogVersion": 1, "assets": []}
        return payload


def refresh_broll_catalog_counts(catalog: dict[str, Any]) -> None:
    assets = [item for item in catalog.get("assets") or [] if isinstance(item, dict)]
    catalog["assetCount"] = len(assets)
    catalog["uniqueAssetCount"] = sum(1 for item in assets if not item.get("duplicateOf"))
    catalog["duplicateCount"] = sum(1 for item in assets if item.get("duplicateOf"))
    catalog["portraitCount"] = sum(1 for item in assets if item.get("portrait"))
    catalog["brollEligibleCount"] = sum(
        1 for item in assets if item.get("useMode") == "ready" and item.get("safeShots")
    )
    catalog["totalDurationSeconds"] = round(
        sum(max(0.0, float(item.get("durationSeconds") or 0.0)) for item in assets), 3
    )
    source_groups: dict[str, int] = {}
    for item in assets:
        group = str(item.get("sourceGroup") or "未分类")
        source_groups[group] = source_groups.get(group, 0) + 1
    catalog["sourceGroups"] = source_groups


def save_broll_catalog(catalog: dict[str, Any]) -> None:
    with BROLL_LOCK:
        refresh_broll_catalog_counts(catalog)
        catalog["catalogVersion"] = int(catalog.get("catalogVersion") or 0) + 1
        catalog["updatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        temporary = BROLL_INDEX.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        temporary.replace(BROLL_INDEX)


def public_broll_asset(item: dict[str, Any]) -> dict[str, Any]:
    asset_id = str(item.get("id") or "")
    display_tags = item.get("displayTags")
    tags = (
        [str(value) for value in display_tags if str(value).strip()]
        if isinstance(display_tags, list)
        else list(dict.fromkeys(
            str(value)
            for key in ("sceneTags", "emotionTags", "subjectTags", "actionTags", "themeTags")
            for value in (item.get(key) or [])
            if str(value).strip()
        ))
    )
    return {
        "id": asset_id,
        "name": str(item.get("displayName") or item.get("filename") or asset_id),
        "summary": str(item.get("visualSummary") or "待整理素材"),
        "category": str(item.get("primaryCategory") or "未分类"),
        "sourceGroup": str(item.get("sourceGroup") or "未分类"),
        "tags": tags,
        "duration": float(item.get("durationSeconds") or 0.0),
        "width": int(item.get("width") or 0),
        "height": int(item.get("height") or 0),
        "useMode": str(item.get("useMode") or "review"),
        "usable": bool(item.get("safeShots")) and item.get("useMode") == "ready",
        "uploaded": str(item.get("sourceGroup") or "") == "用户上传",
        "posterUrl": f"/api/broll-media?id={urllib.parse.quote(asset_id)}&kind=poster",
        "videoUrl": f"/api/broll-media?id={urllib.parse.quote(asset_id)}&kind=video",
        "personId": str(item.get("personId") or ""),
        "createdAt": str(item.get("createdAt") or ""),
    }


def update_broll_asset(asset_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    name = re.sub(r"\s+", " ", str(payload.get("name") or "")).strip()[:120]
    category = re.sub(r"\s+", " ", str(payload.get("category") or "")).strip()[:60]
    raw_tags = payload.get("tags")
    if isinstance(raw_tags, list):
        tag_values = raw_tags
    else:
        tag_values = re.split(r"[,，、\n]+", str(raw_tags or ""))
    tags = list(dict.fromkeys(
        re.sub(r"\s+", " ", str(value)).strip()[:30]
        for value in tag_values
        if re.sub(r"\s+", " ", str(value)).strip()
    ))[:20]
    use_mode = str(payload.get("useMode") or "ready")
    if use_mode not in {"ready", "review", "disabled"}:
        raise ValueError("素材调用状态无效。")
    with BROLL_LOCK:
        catalog = load_broll_catalog()
        record = next(
            (item for item in catalog.get("assets") or [] if str(item.get("id") or "") == asset_id),
            None,
        )
        if record is None:
            raise ValueError("没有找到这条 B-roll 素材。")
        if name:
            record["displayName"] = name
        if category:
            record["primaryCategory"] = category
        record["displayTags"] = tags
        record["useMode"] = use_mode
        record["usable"] = bool(record.get("safeShots")) and use_mode == "ready"
        record["brollEligible"] = record["usable"]
        record["reviewStatus"] = {
            "ready": "人工确认可调用", "review": "等待人工审核", "disabled": "人工暂停调用"
        }[use_mode]
        if "personId" in payload:
            record["personId"] = normalize_person_id(payload.get("personId"))
        record["searchText"] = " ".join([
            str(record.get("visualSummary") or ""),
            str(record.get("primaryCategory") or ""),
            *tags,
        ]).strip()
        save_broll_catalog(catalog)
        BROLL_EMBEDDING_CACHE.unlink(missing_ok=True)
        return public_broll_asset(record)


def delete_broll_asset(asset_id: str) -> None:
    with QUEUE_LOCK:
        dependent = next(
            (
                item for item in QUEUE_ITEMS
                if item.get("status") in {"pending", "running"}
                and bool((item.get("payload") or {}).get("brollEnabled"))
            ),
            None,
        )
    if dependent is not None:
        raise ValueError(
            f"队列任务“{dependent.get('title') or '未命名任务'}”启用了 B-roll，"
            "为避免生成中素材变化，请等该任务完成后再删除。"
        )
    with BROLL_LOCK:
        catalog = load_broll_catalog()
        record = next(
            (item for item in catalog.get("assets") or [] if str(item.get("id") or "") == asset_id),
            None,
        )
        if record is None:
            raise ValueError("没有找到要删除的 B-roll 素材。")
        catalog["assets"] = [
            item for item in catalog.get("assets") or []
            if str(item.get("id") or "") != asset_id
        ]
        save_broll_catalog(catalog)
        if str(record.get("sourceGroup") or "") == "用户上传":
            media_path = Path(str(record.get("path") or ""))
            try:
                media_path.resolve().relative_to(BROLL_UPLOAD_DIR.resolve())
            except (OSError, ValueError):
                pass
            else:
                media_path.unlink(missing_ok=True)
            thumbnail_dir = BROLL_UPLOAD_THUMBNAIL_DIR / asset_id
            try:
                thumbnail_dir.resolve().relative_to(BROLL_UPLOAD_THUMBNAIL_DIR.resolve())
            except (OSError, ValueError):
                pass
            else:
                shutil.rmtree(thumbnail_dir, ignore_errors=True)
        BROLL_EMBEDDING_CACHE.unlink(missing_ok=True)


def broll_asset_record(asset_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in load_broll_catalog().get("assets") or [] if str(item.get("id") or "") == asset_id),
        None,
    )


def broll_media_path(asset_id: str, kind: str) -> Path | None:
    item = broll_asset_record(asset_id)
    if item is None:
        return None
    if kind == "poster":
        frames = item.get("previewFrames") or []
        if not frames:
            return None
        path = BROLL_DIR / str(frames[0])
    else:
        path = Path(str(item.get("path") or ""))
    return path if path.is_file() else None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_broll_preview_frames(video: Path, asset_id: str, duration: float) -> list[str]:
    output_dir = BROLL_UPLOAD_THUMBNAIL_DIR / asset_id
    output_dir.mkdir(parents=True, exist_ok=True)
    moments = [duration * 0.15, duration * 0.5, duration * 0.85]
    frames: list[str] = []
    for index, moment in enumerate(moments, start=1):
        target = output_dir / f"{index}.jpg"
        completed = subprocess.run(
            [
                str(FFMPEG_EXE), "-loglevel", "error", "-y", "-ss", f"{max(0.0, moment):.3f}",
                "-i", str(video), "-frames:v", "1",
                "-vf", "scale=360:640:force_original_aspect_ratio=increase,crop=360:640",
                "-q:v", "3", str(target),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode == 0 and target.is_file():
            frames.append(str(target.relative_to(BROLL_DIR)).replace("\\", "/"))
    if not frames:
        raise RuntimeError("素材缩略图生成失败。")
    return frames


def analyze_uploaded_broll_shots(video: Path, duration: float) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    completed = subprocess.run(
        [
            str(FFMPEG_EXE), "-hide_banner", "-loglevel", "info", "-i", str(video), "-an",
            "-vf", "select='gt(scene,0.20)',showinfo", "-f", "null", "-",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=max(180, int(duration * 8)),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        raise RuntimeError("素材镜头检测失败。")
    boundaries = [0.0]
    for value in sorted(
        float(item) for item in re.findall(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)", completed.stderr)
    ):
        value = max(0.0, min(duration, value))
        if value - boundaries[-1] >= 0.45 and duration - value >= 0.20:
            boundaries.append(value)
    boundaries.append(duration)
    safe_shots: list[dict[str, Any]] = []
    for shot_index, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        safe_start, safe_end = start + 0.18, end - 0.18
        safe_duration = safe_end - safe_start
        if safe_duration < 4.0:
            continue
        safe_shots.append({
            "shot": shot_index,
            "sceneStart": round(start, 3),
            "sceneEnd": round(end, 3),
            "safeStart": round(safe_start, 3),
            "safeEnd": round(safe_end, 3),
            "safeDuration": round(safe_duration, 3),
            "maxClipSeconds": round(min(7.0, safe_duration), 3),
        })
    analysis = {
        "version": 1,
        "threshold": 0.20,
        "boundaryMarginSeconds": 0.18,
        "boundaryCount": max(0, len(boundaries) - 2),
        "boundaries": [round(value, 3) for value in boundaries],
    }
    return analysis, safe_shots


def classify_broll_frames(frame_paths: list[Path]) -> dict[str, Any]:
    python_exe = hd_venv_python()
    if not (BROLL_CLASSIFIER_MODEL_DIR / "pytorch_model.bin").is_file():
        raise RuntimeError("本地素材视觉分类模型未安装完整。")
    request_path = TEMP_DIR / f"broll_classify_{uuid.uuid4().hex}.json"
    request_path.write_text(json.dumps({
        "modelPath": str(BROLL_CLASSIFIER_MODEL_DIR),
        "imagePaths": [str(path) for path in frame_paths],
    }, ensure_ascii=False), encoding="utf-8")
    try:
        completed = subprocess.run(
            [str(python_exe), str(BROLL_CLASSIFIER), str(request_path)],
            cwd=str(APP_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout or "素材识别失败")[-600:])
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        return json.loads(lines[-1])
    finally:
        request_path.unlink(missing_ok=True)


def add_broll_asset(source: Path, original_name: str) -> dict[str, Any]:
    if not source.is_file() or source.suffix.lower() not in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
        raise ValueError("请选择有效的视频素材。")
    if not FFMPEG_EXE.is_file():
        raise RuntimeError("没有找到素材处理组件。")
    info = video_info(source)
    duration = max(0.0, float(info.get("duration") or 0.0))
    if duration < 4.0:
        raise ValueError("素材至少需要 4 秒连续画面。")
    asset_id = f"U{uuid.uuid4().hex[:12].upper()}"
    destination = BROLL_UPLOAD_DIR / f"{asset_id}{source.suffix.lower()}"
    frame_paths: list[Path] = []
    try:
        shutil.copy2(source, destination)
        preview_frames = extract_broll_preview_frames(destination, asset_id, duration)
        frame_paths = [BROLL_DIR / value for value in preview_frames]
        classification = classify_broll_frames(frame_paths)
        scene_analysis, safe_shots = analyze_uploaded_broll_shots(destination, duration)
        digest = file_sha256(destination)
        catalog = load_broll_catalog()
        duplicate = next(
            (item for item in catalog.get("assets") or [] if str(item.get("sha256") or "") == digest),
            None,
        )
        use_mode = "disabled" if duplicate else ("ready" if safe_shots else "review")
        tags = [
            str(value)
            for key in ("sceneTags", "emotionTags", "subjectTags", "actionTags", "themeTags")
            for value in classification.get(key) or []
        ]
        record = {
            "id": asset_id,
            "sourceGroup": "用户上传",
            "sourceRoot": str(BROLL_UPLOAD_DIR),
            "path": str(destination),
            "filename": Path(original_name).name[:180],
            "extension": destination.suffix.lower(),
            "sizeBytes": destination.stat().st_size,
            "sha256": digest,
            "durationSeconds": round(duration, 3),
            "width": int(info.get("width") or 0),
            "height": int(info.get("height") or 0),
            "fps": round(float(info.get("fps") or 0.0), 3),
            "codec": str(info.get("codec") or ""),
            "portrait": int(info.get("height") or 0) > int(info.get("width") or 0),
            "aspectRatio": round(
                int(info.get("width") or 0) / max(1, int(info.get("height") or 0)), 4
            ),
            "previewFrames": preview_frames,
            "duplicateOf": str(duplicate.get("id")) if duplicate else None,
            **classification,
            "qualityFlags": ["内容重复"] if duplicate else [],
            "usable": bool(safe_shots) and not duplicate,
            "reviewStatus": "自动分类完成" if safe_shots else "没有连续 4 秒安全镜头",
            "useMode": use_mode,
            "sceneAnalysis": scene_analysis,
            "safeShots": safe_shots,
            "brollEligible": bool(safe_shots) and not duplicate,
            "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "searchText": " ".join([
                str(classification.get("visualSummary") or ""),
                str(classification.get("primaryCategory") or ""),
                *tags,
            ]).strip(),
        }
        catalog.setdefault("assets", []).append(record)
        save_broll_catalog(catalog)
        BROLL_EMBEDDING_CACHE.unlink(missing_ok=True)
        return public_broll_asset(record)
    except Exception:
        destination.unlink(missing_ok=True)
        shutil.rmtree(BROLL_UPLOAD_THUMBNAIL_DIR / asset_id, ignore_errors=True)
        raise


def load_persons() -> list[dict[str, Any]]:
    with PERSON_LOCK:
        if not PERSON_INDEX.is_file():
            return []
        try:
            raw = json.loads(PERSON_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return []
        records: list[dict[str, Any]] = []
        for item in raw if isinstance(raw, list) else []:
            if not isinstance(item, dict):
                continue
            person_id = str(item.get("id") or "")
            if not re.fullmatch(r"[a-f0-9]{32}", person_id):
                continue
            records.append({
                "id": person_id,
                "name": str(item.get("name") or "")[:40],
                "createdAt": str(item.get("createdAt") or ""),
            })
        return records


def save_persons(records: list[dict[str, Any]]) -> None:
    with PERSON_LOCK:
        temporary = PERSON_INDEX.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(PERSON_INDEX)


def public_person(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "name": record["name"],
        "createdAt": record.get("createdAt") or "",
    }


def normalize_person_id(value: Any) -> str:
    person_id = str(value or "").strip()
    return person_id if re.fullmatch(r"[a-f0-9]{32}", person_id) else ""


def save_person(payload: dict[str, Any]) -> list[dict[str, Any]]:
    name = re.sub(r"\s+", " ", str(payload.get("name") or "")).strip()
    if not name:
        raise ValueError("请输入人物名称。")
    with PERSON_LOCK:
        records = load_persons()
        person_id = str(payload.get("id") or "")
        record = next((item for item in records if item["id"] == person_id), None) if person_id else None
        if person_id and record is None:
            raise ValueError("没有找到这个人物。")
        if any(item["name"] == name and item["id"] != person_id for item in records):
            raise ValueError("已经有同名的人物。")
        if record is None:
            record = {
                "id": uuid.uuid4().hex,
                "name": name[:40],
                "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            records.append(record)
        else:
            record["name"] = name[:40]
        save_persons(records)
        return load_persons()


def delete_person(person_id: str) -> None:
    with PERSON_LOCK:
        records = load_persons()
        record = next((item for item in records if item["id"] == person_id), None)
        if record is None:
            raise ValueError("没有找到这个人物。")
        save_persons([item for item in records if item["id"] != person_id])
    voice_records = load_voice_records()
    voice_changed = False
    for item in voice_records:
        if item.get("personId") == person_id:
            item["personId"] = ""
            voice_changed = True
    if voice_changed:
        save_voice_records(voice_records)
    avatar_records = load_avatar_records()
    avatar_changed = False
    for item in avatar_records:
        if item.get("personId") == person_id:
            item["personId"] = ""
            avatar_changed = True
    if avatar_changed:
        save_avatar_records(avatar_records)
    catalog = load_broll_catalog()
    broll_changed = False
    for item in catalog.get("assets") or []:
        if isinstance(item, dict) and str(item.get("personId") or "") == person_id:
            item["personId"] = ""
            broll_changed = True
    if broll_changed:
        save_broll_catalog(catalog)


def set_asset_person(kind: str, asset_id: str, person_id: str) -> None:
    if kind not in {"voice", "avatar", "broll"}:
        raise ValueError("不支持的素材类型。")
    if person_id and not any(item["id"] == person_id for item in load_persons()):
        raise ValueError("没有找到这个人物。")
    if kind == "voice":
        records = load_voice_records()
        record = next((item for item in records if item["id"] == asset_id), None)
        if record is None:
            raise ValueError("没有找到这条素材。")
        record["personId"] = person_id
        save_voice_records(records)
    elif kind == "avatar":
        records = load_avatar_records()
        record = next((item for item in records if item["id"] == asset_id), None)
        if record is None:
            raise ValueError("没有找到这条素材。")
        record["personId"] = person_id
        save_avatar_records(records)
    else:
        catalog = load_broll_catalog()
        record = next(
            (
                item for item in catalog.get("assets") or []
                if str(item.get("id") or "") == asset_id
            ),
            None,
        )
        if record is None:
            raise ValueError("没有找到这条素材。")
        record["personId"] = person_id
        save_broll_catalog(catalog)


def load_avatar_records() -> list[dict[str, Any]]:
    with AVATAR_LOCK:
        if not AVATAR_INDEX.is_file():
            return []
        try:
            raw = json.loads(AVATAR_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return []
        records: list[dict[str, Any]] = []
        metadata_changed = False
        for item in raw if isinstance(raw, list) else []:
            if not isinstance(item, dict):
                continue
            avatar_id = str(item.get("id") or "")
            video_name = str(item.get("video") or "")
            poster_name = str(item.get("poster") or "")
            if not re.fullmatch(r"[a-f0-9]{32}", avatar_id):
                continue
            if Path(video_name).name != video_name or not (AVATAR_DIR / video_name).is_file():
                continue
            if poster_name and Path(poster_name).name != poster_name:
                poster_name = ""
            stored_duration = max(0.0, float(item.get("duration") or 0.0))
            if stored_duration <= 0.0:
                try:
                    stored_duration = max(
                        0.0, float(video_info(AVATAR_DIR / video_name).get("duration") or 0.0)
                    )
                    metadata_changed = metadata_changed or stored_duration > 0.0
                except Exception:
                    stored_duration = 0.0
            records.append({
                "id": avatar_id,
                "name": str(item.get("name") or "未命名形象")[:80],
                "video": video_name,
                "poster": poster_name,
                "personId": normalize_person_id(item.get("personId")),
                "createdAt": str(item.get("createdAt") or ""),
                "duration": stored_duration,
                "usageCount": max(0, int(item.get("usageCount") or 0)),
                "lastStartOffset": max(0.0, float(item.get("lastStartOffset") or 0.0)),
                "recentStartOffsets": [
                    max(0.0, float(value))
                    for value in (item.get("recentStartOffsets") or [])[-24:]
                    if isinstance(value, (int, float))
                ],
            })
        if metadata_changed:
            save_avatar_records(records)
        return records


def save_avatar_records(records: list[dict[str, Any]]) -> None:
    with AVATAR_LOCK:
        temporary = AVATAR_INDEX.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(AVATAR_INDEX)


def public_avatar(record: dict[str, Any]) -> dict[str, Any]:
    avatar_id = record["id"]
    return {
        "id": avatar_id,
        "name": record["name"],
        "videoPath": str((AVATAR_DIR / record["video"]).resolve()),
        "posterUrl": f"/api/avatar-media?id={avatar_id}&kind=poster" if record.get("poster") else None,
        "videoUrl": f"/api/avatar-media?id={avatar_id}&kind=video",
        "personId": record.get("personId") or "",
        "createdAt": record.get("createdAt") or "",
        "duration": float(record.get("duration") or 0.0),
        "usageCount": int(record.get("usageCount") or 0),
        "lastStartOffset": float(record.get("lastStartOffset") or 0.0),
    }


def add_avatar(source: Path, name: str | None = None, person_id: str = "") -> dict[str, Any]:
    if not source.is_file() or source.suffix.lower() not in {".mp4", ".mov", ".avi", ".mkv"}:
        raise ValueError("请选择有效的数字人视频。")
    avatar_id = uuid.uuid4().hex
    video_name = f"{avatar_id}{source.suffix.lower()}"
    poster_name = f"{avatar_id}.jpg"
    video_path = AVATAR_DIR / video_name
    poster_path = AVATAR_DIR / poster_name
    source_info = video_info(source)
    try:
        shutil.copy2(source, video_path)
        if FFMPEG_EXE.exists():
            subprocess.run(
                [str(FFMPEG_EXE), "-loglevel", "error", "-y", "-ss", "0.3", "-i", str(video_path),
                 "-frames:v", "1", "-vf", "scale=480:-2", "-q:v", "3", str(poster_path)],
                capture_output=True, timeout=120,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
    except Exception:
        video_path.unlink(missing_ok=True)
        poster_path.unlink(missing_ok=True)
        raise
    record = {
        "id": avatar_id,
        "name": (name or source.stem or "未命名形象").strip()[:80],
        "video": video_name,
        "poster": poster_name if poster_path.is_file() else "",
        "personId": normalize_person_id(person_id),
        "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": max(0.0, float(source_info.get("duration") or 0.0)),
        "usageCount": 0,
        "lastStartOffset": 0.0,
        "recentStartOffsets": [],
    }
    records = load_avatar_records()
    records.append(record)
    save_avatar_records(records)
    return public_avatar(record)


def rename_avatar(avatar_id: str, new_name: str) -> list[dict[str, Any]]:
    name = re.sub(r"\s+", " ", new_name).strip()
    if not name:
        raise ValueError("请输入数字人形象名称。")
    with AVATAR_LOCK:
        records = load_avatar_records()
        record = next((item for item in records if item["id"] == avatar_id), None)
        if record is None:
            raise ValueError("没有找到要改名的数字人形象。")
        record["name"] = name[:80]
        save_avatar_records(records)
        return [public_avatar(item) for item in records]


def delete_avatar(avatar_id: str) -> list[dict[str, Any]]:
    with AVATAR_LOCK:
        records = load_avatar_records()
        record = next((item for item in records if item["id"] == avatar_id), None)
        if record is None:
            raise ValueError("没有找到要删除的数字人形象。")
        remaining = [item for item in records if item["id"] != avatar_id]
        save_avatar_records(remaining)
        for key in ("video", "poster"):
            filename = str(record.get(key) or "")
            if filename and Path(filename).name == filename:
                (AVATAR_DIR / filename).unlink(missing_ok=True)
        return [public_avatar(item) for item in remaining]


def avatar_media_path(avatar_id: str, kind: str) -> Path | None:
    record = next((item for item in load_avatar_records() if item["id"] == avatar_id), None)
    if record is None:
        return None
    filename = record.get("poster") if kind == "poster" else record.get("video")
    if not filename:
        return None
    path = AVATAR_DIR / str(filename)
    return path if path.is_file() else None


class _WindowsDataBlob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def windows_crypto_libraries() -> tuple[Any, Any]:
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(_WindowsDataBlob), wintypes.LPCWSTR,
        ctypes.POINTER(_WindowsDataBlob), ctypes.c_void_p, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(_WindowsDataBlob),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(_WindowsDataBlob), ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(_WindowsDataBlob), ctypes.c_void_p, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(_WindowsDataBlob),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    return crypt32, kernel32


def protect_local_secret(value: str) -> str:
    """Encrypt a secret for this Windows computer with DPAPI."""
    if not value:
        return ""
    raw = value.encode("utf-8")
    source_buffer = ctypes.create_string_buffer(raw)
    source = _WindowsDataBlob(
        len(raw), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_ubyte))
    )
    destination = _WindowsDataBlob()
    crypt32, kernel32 = windows_crypto_libraries()
    if not crypt32.CryptProtectData(
        ctypes.byref(source), "LocalDigitalHuman", None, None, None,
        0x05, ctypes.byref(destination),
    ):
        error = ctypes.WinError(ctypes.get_last_error())
        raise RuntimeError(f"API Key 无法写入 Windows 安全存储：{error}")
    try:
        encrypted = ctypes.string_at(destination.pbData, destination.cbData)
        return base64.b64encode(encrypted).decode("ascii")
    finally:
        kernel32.LocalFree(destination.pbData)


def unprotect_local_secret(value: str) -> str:
    if not value:
        return ""
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
        source_buffer = ctypes.create_string_buffer(raw)
        source = _WindowsDataBlob(
            len(raw), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_ubyte))
        )
        destination = _WindowsDataBlob()
        crypt32, kernel32 = windows_crypto_libraries()
        if not crypt32.CryptUnprotectData(
            ctypes.byref(source), None, None, None, None,
            0x05, ctypes.byref(destination),
        ):
            return ""
        try:
            return ctypes.string_at(destination.pbData, destination.cbData).decode("utf-8")
        finally:
            kernel32.LocalFree(destination.pbData)
    except Exception:
        return ""


def normalize_elevenlabs_settings(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}

    def ratio(key: str, default: float) -> float:
        try:
            return max(0.0, min(1.0, float(source.get(key, default))))
        except (TypeError, ValueError):
            return default

    return {
        "stability": ratio("stability", 0.5),
        "similarityBoost": ratio("similarityBoost", 0.75),
        "style": ratio("style", 0.0),
        "speakerBoost": bool(source.get("speakerBoost", True)),
    }


def normalize_elevenlabs_model(record: Any) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None
    model_id = str(record.get("modelId") or record.get("model_id") or "").strip()[:100]
    if not model_id:
        return None
    try:
        max_characters = int(
            record.get("maxCharacters")
            or record.get("maximum_text_length_per_request")
            or record.get("max_characters_request_subscribed_user")
            or 10000
        )
    except (TypeError, ValueError):
        max_characters = 10000
    return {
        "modelId": model_id,
        "name": str(record.get("name") or model_id)[:100],
        "description": str(record.get("description") or "")[:240],
        "maxCharacters": max(100, min(100000, max_characters)),
        "recommended": bool(record.get("recommended", model_id == "eleven_multilingual_v2")),
        "supportsStyle": bool(record.get("supportsStyle", record.get("can_use_style", True))),
        "supportsSpeakerBoost": bool(
            record.get("supportsSpeakerBoost", record.get("can_use_speaker_boost", True))
        ),
    }


def normalize_elevenlabs_remote_voice(record: Any) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None
    voice_id = str(record.get("voiceId") or record.get("voice_id") or "").strip()[:200]
    if not voice_id:
        return None
    return {
        "voiceId": voice_id,
        "name": str(record.get("name") or "未命名声音")[:100],
        "category": str(record.get("category") or "")[:50],
        "previewUrl": str(record.get("previewUrl") or record.get("preview_url") or "")[:1000],
    }


def load_elevenlabs_accounts() -> list[dict[str, Any]]:
    with ELEVENLABS_ACCOUNT_LOCK:
        if not ELEVENLABS_ACCOUNT_INDEX.is_file():
            return []
        try:
            raw = json.loads(ELEVENLABS_ACCOUNT_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return []
        records: list[dict[str, Any]] = []
        for item in raw if isinstance(raw, list) else []:
            if not isinstance(item, dict):
                continue
            account_id = str(item.get("id") or "")
            if not re.fullmatch(r"[a-f0-9]{32}", account_id):
                continue
            models = [
                model for model in
                (normalize_elevenlabs_model(value) for value in item.get("models") or [])
                if model is not None
            ]
            voices = [
                voice for voice in
                (normalize_elevenlabs_remote_voice(value) for value in item.get("voices") or [])
                if voice is not None
            ]
            subscription = item.get("subscription") if isinstance(item.get("subscription"), dict) else {}
            secret = str(item.get("secret") or "")
            status = str(item.get("status") or ("unchecked" if secret else "unbound"))
            if status not in {"unbound", "unchecked", "ready", "error"}:
                status = "unchecked" if secret else "unbound"
            if not secret:
                status = "unbound"
            try:
                priority = max(1, min(99, int(item.get("priority") or 10)))
            except (TypeError, ValueError):
                priority = 10
            records.append({
                "id": account_id,
                "name": str(item.get("name") or "ElevenLabs 账号")[:80],
                "secret": secret,
                "keyPreview": str(item.get("keyPreview") or "")[-8:],
                "enabled": bool(item.get("enabled", True)),
                "priority": priority,
                "status": status,
                "error": str(item.get("error") or "")[:300],
                "subscription": {
                    "tier": str(subscription.get("tier") or "")[:50],
                    "status": str(subscription.get("status") or "")[:50],
                    "characterCount": int(subscription.get("characterCount") or 0),
                    "characterLimit": int(subscription.get("characterLimit") or 0),
                    "nextReset": int(subscription.get("nextReset") or 0),
                    "allowedToExtend": bool(subscription.get("allowedToExtend")),
                },
                "models": models,
                "voices": voices[:500],
                "createdAt": str(item.get("createdAt") or ""),
                "updatedAt": str(item.get("updatedAt") or ""),
                "lastCheckedAt": str(item.get("lastCheckedAt") or ""),
            })
        return records


def save_elevenlabs_accounts(records: list[dict[str, Any]]) -> None:
    with ELEVENLABS_ACCOUNT_LOCK:
        temporary = ELEVENLABS_ACCOUNT_INDEX.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(ELEVENLABS_ACCOUNT_INDEX)


def public_elevenlabs_account(record: dict[str, Any]) -> dict[str, Any]:
    subscription = dict(record.get("subscription") or {})
    limit = int(subscription.get("characterLimit") or 0)
    used = int(subscription.get("characterCount") or 0)
    subscription["usagePercent"] = round(used / limit * 100, 1) if limit > 0 else 0
    return {
        "id": record["id"],
        "name": record["name"],
        "hasKey": bool(record.get("secret")),
        "keyPreview": record.get("keyPreview") or "",
        "enabled": bool(record.get("enabled", True)),
        "priority": int(record.get("priority") or 10),
        "status": record.get("status") or "unbound",
        "error": record.get("error") or "",
        "subscription": subscription,
        "models": list(record.get("models") or []),
        "voices": list(record.get("voices") or []),
        "createdAt": record.get("createdAt") or "",
        "updatedAt": record.get("updatedAt") or "",
        "lastCheckedAt": record.get("lastCheckedAt") or "",
    }


def elevenlabs_api_json(path: str, api_key: str, timeout: int = 30) -> Any:
    url = f"https://api.elevenlabs.io{path}"
    try:
        return http_json(url, timeout=timeout, headers={"xi-api-key": api_key})
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        message = detail
        try:
            parsed = json.loads(detail)
            nested = parsed.get("detail") if isinstance(parsed, dict) else None
            if isinstance(nested, dict):
                message = str(nested.get("message") or nested.get("status") or detail)
            elif nested:
                message = str(nested)
        except Exception:
            pass
        if exc.code in {401, 403}:
            raise ValueError("API Key 无效、权限不足或已被停用。") from exc
        raise RuntimeError(f"ElevenLabs 返回 {exc.code}：{message[:240]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"无法连接 ElevenLabs，请检查网络或代理设置：{exc.reason}") from exc


def save_elevenlabs_account(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    account_id = str(payload.get("id") or "").strip()
    if account_id and not re.fullmatch(r"[a-f0-9]{32}", account_id):
        raise ValueError("ElevenLabs 账号编号无效。")
    records = load_elevenlabs_accounts()
    record = next((item for item in records if item["id"] == account_id), None)
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    if record is None:
        account_id = uuid.uuid4().hex
        record = {
            "id": account_id,
            "name": "ElevenLabs 账号",
            "secret": "",
            "keyPreview": "",
            "enabled": True,
            "priority": 10,
            "status": "unbound",
            "error": "",
            "subscription": {},
            "models": [],
            "voices": [],
            "createdAt": now,
            "updatedAt": now,
            "lastCheckedAt": "",
        }
        records.append(record)
    name = re.sub(r"\s+", " ", str(payload.get("name") or "")).strip()
    if not name:
        raise ValueError("请输入账号名称。")
    record["name"] = name[:80]
    record["enabled"] = bool(payload.get("enabled", True))
    try:
        record["priority"] = max(1, min(99, int(payload.get("priority") or 10)))
    except (TypeError, ValueError):
        record["priority"] = 10
    api_key = str(payload.get("apiKey") or "").strip()
    if bool(payload.get("clearKey")):
        record["secret"] = ""
        record["keyPreview"] = ""
        record["status"] = "unbound"
        record["error"] = ""
        record["subscription"] = {}
        record["models"] = []
        record["voices"] = []
    elif api_key:
        record["secret"] = protect_local_secret(api_key)
        record["keyPreview"] = api_key[-4:]
        record["status"] = "unchecked"
        record["error"] = ""
    record["updatedAt"] = now
    save_elevenlabs_accounts(records)
    warning = ""
    if api_key and bool(payload.get("testConnection", True)):
        try:
            record = sync_elevenlabs_account(account_id)
        except Exception as exc:
            warning = str(exc)
            records = load_elevenlabs_accounts()
            record = next(item for item in records if item["id"] == account_id)
    return record, warning


def sync_elevenlabs_account(account_id: str) -> dict[str, Any]:
    records = load_elevenlabs_accounts()
    record = next((item for item in records if item["id"] == account_id), None)
    if record is None:
        raise ValueError("没有找到这个 ElevenLabs 账号。")
    api_key = unprotect_local_secret(str(record.get("secret") or ""))
    if not api_key:
        raise ValueError("这个账号还没有绑定 API Key。")
    try:
        subscription_raw = elevenlabs_api_json("/v1/user/subscription", api_key)
        models_raw = elevenlabs_api_json("/v1/models", api_key)
        voices_raw = elevenlabs_api_json(
            "/v2/voices?page_size=100&include_total_count=true&sort=name&sort_direction=asc",
            api_key,
        )
        subscription = subscription_raw if isinstance(subscription_raw, dict) else {}
        models = [
            item for item in
            (normalize_elevenlabs_model(value) for value in models_raw if isinstance(models_raw, list))
            if item is not None and any(
                str(value.get("model_id") or "") == item["modelId"]
                and bool(value.get("can_do_text_to_speech", True))
                for value in models_raw if isinstance(value, dict)
            )
        ]
        remote_values = voices_raw.get("voices") if isinstance(voices_raw, dict) else []
        voices = [
            item for item in
            (normalize_elevenlabs_remote_voice(value) for value in remote_values or [])
            if item is not None
        ]
        record["subscription"] = {
            "tier": str(subscription.get("tier") or ""),
            "status": str(subscription.get("status") or ""),
            "characterCount": int(subscription.get("character_count") or 0),
            "characterLimit": int(subscription.get("character_limit") or 0),
            "nextReset": int(subscription.get("next_character_count_reset_unix") or 0),
            # payg（按量付费）账号超出 character_limit 后走预购 credits 扣费，
            # limit-count 不代表真实余额，前端按 tier 区分显示口径
            "allowedToExtend": bool(
                subscription.get("allowed_to_extend_character_limit")
                or subscription.get("can_extend_character_limit")
            ),
        }
        record["models"] = models
        record["voices"] = voices[:500]
        record["status"] = "ready"
        record["error"] = ""
        record["lastCheckedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
        record["updatedAt"] = record["lastCheckedAt"]
        save_elevenlabs_accounts(records)
        return record
    except Exception as exc:
        record["status"] = "error"
        record["error"] = str(exc)[:300]
        record["lastCheckedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
        record["updatedAt"] = record["lastCheckedAt"]
        save_elevenlabs_accounts(records)
        raise


def delete_elevenlabs_account(account_id: str) -> None:
    with QUEUE_LOCK:
        queued = next(
            (
                item for item in QUEUE_ITEMS
                if item.get("status") in {"pending", "paused", "running"}
                and str((item.get("payload") or {}).get("elevenAccountId") or "") == account_id
            ),
            None,
        )
    if queued is not None:
        raise ValueError(f"这个账号正在被队列任务“{queued.get('title') or '未命名任务'}”使用，暂时不能删除。")
    records = load_elevenlabs_accounts()
    if not any(item["id"] == account_id for item in records):
        raise ValueError("没有找到这个 ElevenLabs 账号。")
    save_elevenlabs_accounts([item for item in records if item["id"] != account_id])

    voice_records = load_voice_records()
    changed = False
    for voice in voice_records:
        if voice.get("provider") == "elevenlabs" and voice.get("accountId") == account_id:
            voice["accountId"] = ""
            changed = True
    if changed:
        save_voice_records(voice_records)


def elevenlabs_account_can_call_voice(record: dict[str, Any], voice_id: str) -> bool:
    if not voice_id:
        return False
    return any(
        str(voice.get("voiceId") or "") == voice_id
        for voice in record.get("voices") or []
        if isinstance(voice, dict)
    )


def resolve_elevenlabs_account(account_id: str = "", voice_id: str = "") -> tuple[dict[str, Any], str]:
    records = load_elevenlabs_accounts()
    if account_id:
        record = next((item for item in records if item["id"] == account_id), None)
        if record is None:
            raise ValueError("选择的 ElevenLabs 账号已经不存在。")
        if not record.get("enabled", True):
            raise ValueError("选择的 ElevenLabs 账号已停用。")
        api_key = unprotect_local_secret(str(record.get("secret") or ""))
        if not api_key:
            raise ValueError(f"账号“{record['name']}”还没有绑定 API Key。")
        if voice_id and not elevenlabs_account_can_call_voice(record, voice_id):
            raise ValueError(
                f"账号“{record['name']}”不能调用当前声音。请在声音模型页刷新账号，"
                "或在工作台选择拥有该声音的 API 账号。"
            )
        return record, api_key
    candidates: list[tuple[float, int, dict[str, Any], str]] = []
    for record in records:
        if not record.get("enabled", True):
            continue
        api_key = unprotect_local_secret(str(record.get("secret") or ""))
        if not api_key:
            continue
        if voice_id and not elevenlabs_account_can_call_voice(record, voice_id):
            continue
        subscription = record.get("subscription") or {}
        limit = int(subscription.get("characterLimit") or 0)
        used = int(subscription.get("characterCount") or 0)
        usage = used / limit if limit > 0 else 0.0
        candidates.append((usage, int(record.get("priority") or 10), record, api_key))
    if not candidates:
        if voice_id:
            raise ValueError("还没有可调用当前声音的 ElevenLabs API 账号，请先绑定并同步账号。")
        raise ValueError("还没有可用的 ElevenLabs API 账号，请先在声音模型页绑定。")
    _, _, record, api_key = min(candidates, key=lambda item: (item[0], item[1], item[2]["name"]))
    return record, api_key


def record_elevenlabs_usage(account_id: str, characters: int) -> None:
    if not account_id or characters <= 0:
        return
    with ELEVENLABS_ACCOUNT_LOCK:
        records = load_elevenlabs_accounts()
        record = next((item for item in records if item["id"] == account_id), None)
        if record is None:
            return
        subscription = record.get("subscription") or {}
        subscription["characterCount"] = max(
            0, int(subscription.get("characterCount") or 0) + int(characters)
        )
        record["subscription"] = subscription
        record["updatedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_elevenlabs_accounts(records)


def elevenlabs_config_snapshot() -> dict[str, Any]:
    accounts = [public_elevenlabs_account(item) for item in load_elevenlabs_accounts()]
    discovered: dict[str, dict[str, Any]] = {
        item["modelId"]: dict(item) for item in ELEVENLABS_DEFAULT_MODELS
    }
    for account in accounts:
        for model in account.get("models") or []:
            discovered[model["modelId"]] = model
    return {
        "ok": True,
        "accounts": accounts,
        "models": list(discovered.values()),
        "generationModes": ELEVENLABS_GENERATION_MODES,
        "outputFormats": ELEVENLABS_OUTPUT_FORMATS,
        "readyAccounts": sum(1 for item in accounts if item["status"] == "ready" and item["enabled"]),
    }


def load_voice_records() -> list[dict[str, Any]]:
    with VOICE_LIBRARY_LOCK:
        if not VOICE_INDEX.is_file():
            return []
        try:
            raw = json.loads(VOICE_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return []
        records: list[dict[str, Any]] = []
        for item in raw if isinstance(raw, list) else []:
            if not isinstance(item, dict):
                continue
            voice_id = str(item.get("id") or "")
            provider = str(item.get("provider") or "")
            if not re.fullmatch(r"[a-f0-9]{32}", voice_id) or provider not in {"local", "elevenlabs"}:
                continue
            record = {
                "id": voice_id,
                "name": str(item.get("name") or "未命名声音")[:80],
                "provider": provider,
                "personId": normalize_person_id(item.get("personId")),
                "createdAt": str(item.get("createdAt") or ""),
            }
            if provider == "local":
                sample_name = str(item.get("sample") or "")
                if Path(sample_name).name != sample_name or not (VOICE_LIBRARY_DIR / sample_name).is_file():
                    continue
                preview_name = str(item.get("preview") or "")
                if preview_name and (Path(preview_name).name != preview_name or not (VOICE_LIBRARY_DIR / preview_name).is_file()):
                    preview_name = ""
                status = str(item.get("status") or "ready")
                if status not in {"pending", "ready", "error"}:
                    status = "ready"
                engine = str(item.get("engine") or "v2")
                if engine not in VOICE_ENGINES:
                    engine = "v2"
                record.update({
                    "sample": sample_name,
                    "promptText": str(item.get("promptText") or "")[:500],
                    "preview": preview_name,
                    "status": status,
                    "clonedAt": str(item.get("clonedAt") or ""),
                    "cloneError": str(item.get("cloneError") or "")[:300],
                    "engine": engine,
                })
            else:
                external_id = str(item.get("voiceId") or "").strip()
                if not external_id:
                    continue
                account_id = str(item.get("accountId") or "").strip()
                if account_id and not re.fullmatch(r"[a-f0-9]{32}", account_id):
                    account_id = ""
                model_id = str(item.get("modelId") or "eleven_multilingual_v2").strip()[:100]
                output_format = str(item.get("outputFormat") or "mp3_44100_128")
                if output_format not in ELEVENLABS_OUTPUT_FORMAT_IDS:
                    output_format = "mp3_44100_128"
                record.update({
                    "voiceId": external_id[:200],
                    "accountId": account_id,
                    "modelId": model_id or "eleven_multilingual_v2",
                    "outputFormat": output_format,
                    "settings": normalize_elevenlabs_settings(item.get("settings")),
                    "previewUrl": str(item.get("previewUrl") or "")[:1000],
                    "remoteName": str(item.get("remoteName") or "")[:100],
                    "category": str(item.get("category") or "")[:30],
                })
            records.append(record)
        return records


def save_voice_records(records: list[dict[str, Any]]) -> None:
    with VOICE_LIBRARY_LOCK:
        temporary = VOICE_INDEX.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(VOICE_INDEX)


def public_voice(record: dict[str, Any]) -> dict[str, Any]:
    voice_id = record["id"]
    result = {
        "id": voice_id,
        "name": record["name"],
        "provider": record["provider"],
        "personId": record.get("personId") or "",
        "createdAt": record.get("createdAt") or "",
    }
    if record["provider"] == "local":
        result.update({
            "samplePath": str((VOICE_LIBRARY_DIR / record["sample"]).resolve()),
            "sampleUrl": f"/api/voice-media?id={voice_id}",
            "previewUrl": f"/api/voice-media?id={voice_id}&kind=preview" if record.get("preview") else None,
            "promptText": record.get("promptText") or "",
            "status": record.get("status") or "ready",
            "clonedAt": record.get("clonedAt") or "",
            "cloneError": record.get("cloneError") or "",
            "engine": str(record.get("engine") or "v2"),
            "engineName": VOICE_ENGINE_NAMES.get(str(record.get("engine") or "v2"), "本地引擎"),
        })
    else:
        account_id = str(record.get("accountId") or "")
        account_records = load_elevenlabs_accounts()
        account = next((item for item in account_records if item["id"] == account_id), None)
        automatic_ready = (
            not account_id and any(
                item.get("enabled", True) and item.get("status") == "ready"
                for item in account_records
            )
        )
        status = "ready" if automatic_ready or (account and account.get("status") == "ready") else "unbound"
        if account and account.get("status") == "error":
            status = "error"
        result.update({
            "voiceId": record["voiceId"],
            "accountId": account_id,
            "accountName": account.get("name") if account else "自动选择账号" if not account_id else "账号已删除",
            "accountStatus": account.get("status") if account else "ready" if automatic_ready else "unbound",
            "status": status,
            "modelId": record.get("modelId") or "eleven_multilingual_v2",
            "outputFormat": record.get("outputFormat") or "mp3_44100_128",
            "settings": normalize_elevenlabs_settings(record.get("settings")),
            "previewUrl": record.get("previewUrl") or "",
            "remoteName": record.get("remoteName") or "",
            "category": record.get("category") or "",
        })
    return result


def add_local_voice(source: Path, name: str | None = None, prompt_text: str = "",
                    engine: str = "v2", person_id: str = "") -> dict[str, Any]:
    accepted = {".wav", ".mp3", ".m4a", ".flac", ".aac", ".mp4", ".mov", ".avi", ".mkv"}
    if not source.is_file() or source.suffix.lower() not in accepted:
        raise ValueError("请选择有效的声音或视频文件。")
    if engine not in VOICE_ENGINES:
        engine = "v2"
    if not FFMPEG_EXE.exists():
        raise RuntimeError("没有找到声音处理组件。")
    voice_id = uuid.uuid4().hex
    sample_name = f"{voice_id}.wav"
    sample_path = VOICE_LIBRARY_DIR / sample_name
    completed = subprocess.run(
        [str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(source), "-vn", "-t", "30",
         "-ac", "1", "-ar", "22050", "-c:a", "pcm_s16le", str(sample_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not sample_path.is_file() or sample_path.stat().st_size == 0:
        sample_path.unlink(missing_ok=True)
        raise RuntimeError(f"声音样本处理失败。{completed.stderr[-300:]}")
    record = {
        "id": voice_id,
        "name": (name or source.stem or "未命名声音").strip()[:80],
        "provider": "local",
        "sample": sample_name,
        "promptText": prompt_text.strip()[:500],
        "preview": "",
        "status": "pending",
        "clonedAt": "",
        "cloneError": "",
        "engine": engine,
        "personId": normalize_person_id(person_id),
        "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    records = load_voice_records()
    records.append(record)
    save_voice_records(records)
    return public_voice(record)


def transcribe_voice_sample(voice_id: str) -> str:
    record = next(
        (item for item in load_voice_records()
         if item["id"] == voice_id and item["provider"] == "local"),
        None,
    )
    if record is None:
        raise ValueError("没有找到这个本地声音。")
    sample = VOICE_LIBRARY_DIR / record["sample"]
    if not sample.is_file():
        raise ValueError("这个声音的样本文件不存在。")
    if not VOXCPM_PYTHON.is_file() or not TRANSCRIBE_SCRIPT.is_file():
        raise RuntimeError("本地转写组件不存在。")
    wav_path = TEMP_DIR / f"transcribe_{uuid.uuid4().hex}.wav"
    converted = subprocess.run(
        [str(FFMPEG_EXE), "-loglevel", "error", "-y", "-i", str(sample),
         "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav_path)],
        capture_output=True, timeout=120,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if converted.returncode != 0 or not wav_path.is_file() or wav_path.stat().st_size == 0:
        wav_path.unlink(missing_ok=True)
        raise RuntimeError("样本音频处理失败。")
    try:
        completed = subprocess.run(
            [str(VOXCPM_PYTHON), str(TRANSCRIBE_SCRIPT), str(wav_path)],
            cwd=str(APP_DIR),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=900,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        result = {}
        if output_lines:
            try:
                result = json.loads(output_lines[-1])
            except Exception:
                result = {}
        if not result.get("ok"):
            detail = str(result.get("error") or completed.stderr or "转写失败")[-300:]
            raise RuntimeError(detail)
        return str(result.get("text") or "").strip()[:500]
    finally:
        wav_path.unlink(missing_ok=True)


def set_voice_transcript(voice_id: str, prompt_text: str) -> list[dict[str, Any]]:
    records = load_voice_records()
    record = next(
        (item for item in records if item["id"] == voice_id and item["provider"] == "local"),
        None,
    )
    if record is None:
        raise ValueError("没有找到这个本地声音。")
    record["promptText"] = prompt_text.strip()[:500]
    save_voice_records(records)
    return [public_voice(item) for item in records]


def save_elevenlabs_voice(payload: dict[str, Any]) -> dict[str, Any]:
    record_id = str(payload.get("id") or "").strip()
    if record_id and not re.fullmatch(r"[a-f0-9]{32}", record_id):
        raise ValueError("声音编号无效。")
    external_voice_id = str(payload.get("voiceId") or "").strip()
    if not external_voice_id:
        raise ValueError("请输入 ElevenLabs Voice ID。")
    account_id = str(payload.get("accountId") or "").strip()
    if account_id and not any(item["id"] == account_id for item in load_elevenlabs_accounts()):
        raise ValueError("选择的 ElevenLabs 账号不存在。")
    model_id = str(payload.get("modelId") or "eleven_multilingual_v2").strip()[:100]
    if not model_id:
        model_id = "eleven_multilingual_v2"
    output_format = str(payload.get("outputFormat") or "mp3_44100_128")
    if output_format not in ELEVENLABS_OUTPUT_FORMAT_IDS:
        output_format = "mp3_44100_128"
    records = load_voice_records()
    record = next((item for item in records if item["id"] == record_id), None)
    if record is not None and record.get("provider") != "elevenlabs":
        raise ValueError("本地声音不能改成云端声音。")
    if record is None:
        record = {
            "id": uuid.uuid4().hex,
            "provider": "elevenlabs",
            "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        records.append(record)
    remote_voice = None
    if account_id:
        account = next(
            (item for item in load_elevenlabs_accounts() if item["id"] == account_id), None
        )
        remote_voice = next(
            (item for item in (account or {}).get("voices") or []
             if item.get("voiceId") == external_voice_id),
            None,
        )
    record.update({
        "name": (str(payload.get("name") or "").strip() or (remote_voice or {}).get("name") or "ElevenLabs 声音")[:80],
        "voiceId": external_voice_id[:200],
        "accountId": account_id,
        "modelId": model_id,
        "outputFormat": output_format,
        "settings": normalize_elevenlabs_settings(payload.get("settings")),
        "previewUrl": str(payload.get("previewUrl") or (remote_voice or {}).get("previewUrl") or "")[:1000],
        "remoteName": str((remote_voice or {}).get("name") or "")[:100],
        "category": str((remote_voice or {}).get("category") or record.get("category") or "")[:30],
    })
    if "personId" in payload:
        record["personId"] = normalize_person_id(payload.get("personId"))
    save_voice_records(records)
    return public_voice(record)


def add_elevenlabs_voice(name: str, external_voice_id: str) -> dict[str, Any]:
    return save_elevenlabs_voice({"name": name, "voiceId": external_voice_id})


def update_voice_record(voice_id: str, **changes: Any) -> dict[str, Any]:
    with VOICE_LIBRARY_LOCK:
        records = load_voice_records()
        record = next((item for item in records if item["id"] == voice_id), None)
        if record is None or record["provider"] != "local":
            raise ValueError("没有找到要克隆的本地声音。")
        record.update(changes)
        save_voice_records(records)
        return record


def clone_voice_task(voice_id: str) -> None:
    try:
        record = update_voice_record(voice_id, status="pending", cloneError="")
        sample_path = VOICE_LIBRARY_DIR / record["sample"]
        preview_name = f"{voice_id}_clone.wav"
        preview_path = VOICE_LIBRARY_DIR / preview_name
        preview_path.unlink(missing_ok=True)
        update_job("clone", stage="正在准备声音克隆", progress=5)
        generated = generate_local_voice(
            "clone", "你好，这是我的克隆声音。", sample_path,
            record.get("promptText") or "", preview_path, 1.0,
            engine=str(record.get("engine") or "v2"),
        )
        update_voice_record(
            voice_id,
            preview=generated.name,
            status="ready",
            clonedAt=time.strftime("%Y-%m-%d %H:%M:%S"),
            cloneError="",
        )
        update_job(
            "clone", status="done", stage="声音克隆完成", progress=100,
            result=str(generated), audio=str(generated), message="声音已经克隆完成。",
        )
    except Exception as exc:
        try:
            update_voice_record(voice_id, status="error", cloneError=str(exc))
        except Exception:
            pass
        update_job("clone", status="error", stage="声音克隆失败", error=str(exc), message=str(exc))
        append_job_log("clone", traceback.format_exc())
    finally:
        # 克隆拉起的声音服务没人继续用就 5 分钟后自动释放
        schedule_voice_stop(VOICE_LAST_USED)


def delete_voice(voice_id: str) -> list[dict[str, Any]]:
    with VOICE_LIBRARY_LOCK:
        records = load_voice_records()
        record = next((item for item in records if item["id"] == voice_id), None)
        if record is None:
            raise ValueError("没有找到要删除的声音。")
        remaining = [item for item in records if item["id"] != voice_id]
        save_voice_records(remaining)
        for key in ("sample", "preview"):
            filename = str(record.get(key) or "")
            if filename and Path(filename).name == filename:
                (VOICE_LIBRARY_DIR / filename).unlink(missing_ok=True)
        return [public_voice(item) for item in remaining]


def rename_voice(voice_id: str, new_name: str) -> list[dict[str, Any]]:
    name = re.sub(r"\s+", " ", new_name).strip()
    if not name:
        raise ValueError("请输入声音名称。")
    with VOICE_LIBRARY_LOCK:
        records = load_voice_records()
        record = next((item for item in records if item["id"] == voice_id), None)
        if record is None:
            raise ValueError("没有找到要改名的声音。")
        record["name"] = name[:80]
        save_voice_records(records)
        return [public_voice(item) for item in records]


def voice_media_path(voice_id: str, kind: str = "sample") -> Path | None:
    record = next((item for item in load_voice_records() if item["id"] == voice_id), None)
    if record is None or record["provider"] != "local":
        return None
    filename = record.get("preview") if kind == "preview" else record.get("sample")
    if not filename:
        return None
    path = VOICE_LIBRARY_DIR / str(filename)
    return path if path.is_file() else None


def load_music_records() -> list[dict[str, Any]]:
    with MUSIC_LIBRARY_LOCK:
        if not MUSIC_INDEX.is_file():
            return []
        try:
            raw = json.loads(MUSIC_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return []
        records: list[dict[str, Any]] = []
        for item in raw if isinstance(raw, list) else []:
            if not isinstance(item, dict):
                continue
            music_id = str(item.get("id") or "")
            filename = str(item.get("file") or "")
            if not re.fullmatch(r"[a-f0-9]{32}", music_id):
                continue
            if Path(filename).name != filename or not (MUSIC_LIBRARY_DIR / filename).is_file():
                continue
            records.append({
                "id": music_id,
                "name": str(item.get("name") or "未命名音乐")[:100],
                "file": filename,
                "duration": max(0.0, float(item.get("duration") or 0.0)),
                "createdAt": str(item.get("createdAt") or ""),
            })
        return records


def save_music_records(records: list[dict[str, Any]]) -> None:
    with MUSIC_LIBRARY_LOCK:
        temporary = MUSIC_INDEX.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(MUSIC_INDEX)


def public_music(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "name": record["name"],
        "duration": record.get("duration") or 0,
        "audioUrl": f"/api/music-media?id={record['id']}",
        "createdAt": record.get("createdAt") or "",
    }


def add_music(source: Path, name: str | None = None) -> dict[str, Any]:
    accepted = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
    if not source.is_file() or source.suffix.lower() not in accepted:
        raise ValueError("请选择有效的音乐文件。")
    duration = media_duration(source)
    if duration <= 0.1:
        raise ValueError("这个音乐文件没有可读取的音频。")
    music_id = uuid.uuid4().hex
    filename = f"{music_id}{source.suffix.lower()}"
    destination = MUSIC_LIBRARY_DIR / filename
    try:
        shutil.copy2(source, destination)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    record = {
        "id": music_id,
        "name": (name or source.stem or "未命名音乐").strip()[:100],
        "file": filename,
        "duration": round(duration, 3),
        "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    records = load_music_records()
    records.append(record)
    save_music_records(records)
    return public_music(record)


def delete_music(music_id: str) -> list[dict[str, Any]]:
    with MUSIC_LIBRARY_LOCK:
        records = load_music_records()
        record = next((item for item in records if item["id"] == music_id), None)
        if record is None:
            raise ValueError("没有找到要删除的音乐。")
        remaining = [item for item in records if item["id"] != music_id]
        save_music_records(remaining)
        filename = str(record.get("file") or "")
        if filename and Path(filename).name == filename:
            (MUSIC_LIBRARY_DIR / filename).unlink(missing_ok=True)
        return [public_music(item) for item in remaining]


def music_media_path(music_id: str) -> Path | None:
    record = next((item for item in load_music_records() if item["id"] == music_id), None)
    if record is None:
        return None
    path = MUSIC_LIBRARY_DIR / str(record["file"])
    return path if path.is_file() else None


def allowed_media_path(requested: str) -> Path | None:
    try:
        candidate = Path(requested).resolve()
    except Exception:
        return None
    # 工作台"自己录音"上传的文件在 temp/uploads，试听时需要能直接访问
    try:
        candidate.relative_to(UPLOAD_DIR.resolve())
        if candidate.is_file():
            return candidate
    except (ValueError, OSError):
        pass
    with STATE_LOCK:
        allowed = {
            str(Path(value).resolve()).lower()
            for job in JOBS.values()
            for value in (job.get("result"), job.get("audio"))
            if value
        }
    if str(candidate).lower() not in allowed or not candidate.is_file():
        return None
    return candidate


class AppHandler(BaseHTTPRequestHandler):
    server_version = "LocalDigitalHuman/0.1"

    def log_message(self, format_string: str, *args: Any) -> None:
        return

    def send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, Any]:
        length = min(int(self.headers.get("Content-Length", "0") or 0), 10_000_000)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def read_upload(self, allowed_suffixes: set[str], max_bytes: int) -> tuple[Path, str, dict[str, str]]:
        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", "0") or 0)
        if "multipart/form-data" not in content_type.lower():
            raise ValueError("上传格式无效。")
        if content_length <= 0:
            raise ValueError("没有收到上传文件。")
        if content_length > max_bytes:
            raise ValueError("上传文件过大。")

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(content_length),
            },
            keep_blank_values=True,
        )
        if "file" not in form:
            raise ValueError("没有收到上传文件。")
        upload = form["file"]
        if isinstance(upload, list):
            upload = upload[0]
        original_name = Path(str(getattr(upload, "filename", "") or "upload.bin")).name
        suffix = Path(original_name).suffix.lower()
        if suffix not in allowed_suffixes:
            raise ValueError("不支持这个文件格式。")
        stream = getattr(upload, "file", None)
        if stream is None:
            raise ValueError("上传文件无法读取。")

        destination = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
        try:
            with destination.open("wb") as target:
                shutil.copyfileobj(stream, target, 1024 * 1024)
            if not destination.is_file() or destination.stat().st_size <= 0:
                raise ValueError("上传文件为空。")
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        fields = {
            "name": str(form.getfirst("name", "") or "").strip(),
            "promptText": str(form.getfirst("promptText", "") or "").strip(),
            "engine": str(form.getfirst("engine", "") or "").strip(),
            "personId": str(form.getfirst("personId", "") or "").strip(),
        }
        return destination, original_name, fields

    def send_static(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8" if mime.startswith("text/") else mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def send_media(self, path: Path) -> None:
        size = path.stat().st_size
        start, end = 0, size - 1
        range_header = self.headers.get("Range", "")
        if range_header.startswith("bytes="):
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if match:
                if match.group(1):
                    start = int(match.group(1))
                if match.group(2):
                    end = min(end, int(match.group(2)))
        length = max(0, end - start + 1)
        self.send_response(206 if range_header else 200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if range_header:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with path.open("rb") as stream:
            stream.seek(start)
            remaining = length
            while remaining > 0:
                chunk = stream.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_static(APP_DIR / "index.html")
        elif parsed.path == "/styles.css":
            self.send_static(APP_DIR / "styles.css")
        elif parsed.path == "/app.js":
            self.send_static(APP_DIR / "app.js")
        elif parsed.path == "/ui-fx.js":
            self.send_static(APP_DIR / "ui-fx.js")
        elif parsed.path == "/assets/app-icon.png":
            self.send_static(APP_DIR / "assets" / "app-icon.png")
        elif parsed.path == "/assets/app-icon.ico":
            self.send_static(APP_DIR / "assets" / "app-icon.ico")
        elif parsed.path == "/api/ping":
            self.send_json({"ok": True})
        elif parsed.path == "/api/status":
            modules = {
                name: (MODULES_ROOT / name).exists()
                for name in ("voiceV2Module", "humanModule", "hdModule")
            }
            self.send_json({
                "ok": True,
                "gpu": gpu_status(),
                "modules": modules,
                "modulesRoot": str(MODULES_ROOT),
                "defaultOutput": str(DEFAULT_OUTPUT),
                "components": component_status(),
            })
        elif parsed.path == "/api/setup/steps":
            self.send_json({
                "ok": True,
                "steps": [
                    {**meta, "id": step_id, "installed": setup_step_installed(step_id)}
                    for step_id, meta in SETUP_STEP_META.items()
                ],
                "running": setup_running(),
                "gpu": gpu_status(),
                "components": component_status(),
                "bundle": bundle_snapshot(),
            })
        elif parsed.path == "/api/job":
            kind = urllib.parse.parse_qs(parsed.query).get("kind", ["main"])[0]
            self.send_json(snapshot_job(kind))
        elif parsed.path == "/api/queue":
            self.send_json(queue_public_snapshot())
        elif parsed.path == "/api/avatars":
            self.send_json({"ok": True, "avatars": [public_avatar(item) for item in load_avatar_records()]})
        elif parsed.path == "/api/persons":
            self.send_json({"ok": True, "persons": [public_person(item) for item in load_persons()]})
        elif parsed.path == "/api/broll":
            catalog = load_broll_catalog()
            assets = [public_broll_asset(item) for item in catalog.get("assets") or []]
            categories = sorted({item["category"] for item in assets if item["category"]})
            self.send_json({
                "ok": True,
                "assets": assets,
                "categories": categories,
                "total": len(assets),
                "usable": sum(1 for item in assets if item["usable"]),
            })
        elif parsed.path == "/api/broll-media":
            query = urllib.parse.parse_qs(parsed.query)
            kind = query.get("kind", ["video"])[0]
            media = broll_media_path(query.get("id", [""])[0], kind)
            if media is None:
                self.send_error(404)
            elif kind == "poster":
                self.send_static(media)
            else:
                self.send_media(media)
        elif parsed.path == "/api/voices":
            self.send_json({"ok": True, "voices": [public_voice(item) for item in load_voice_records()]})
        elif parsed.path == "/api/elevenlabs/config":
            self.send_json(elevenlabs_config_snapshot())
        elif parsed.path == "/api/music":
            query = urllib.parse.parse_qs(parsed.query)
            search = str(query.get("q", [""])[0] or "").strip().casefold()
            records = load_music_records()
            if search:
                records = [item for item in records if search in str(item.get("name") or "").casefold()]
            self.send_json({"ok": True, "music": [public_music(item) for item in records]})
        elif parsed.path == "/api/music-media":
            query = urllib.parse.parse_qs(parsed.query)
            media = music_media_path(query.get("id", [""])[0])
            if media is None:
                self.send_error(404)
            else:
                self.send_media(media)
        elif parsed.path == "/api/voice-media":
            query = urllib.parse.parse_qs(parsed.query)
            voice_id = query.get("id", [""])[0]
            media = voice_media_path(voice_id, query.get("kind", ["sample"])[0])
            if media is None:
                self.send_error(404)
            else:
                self.send_media(media)
        elif parsed.path == "/api/avatar-media":
            query = urllib.parse.parse_qs(parsed.query)
            avatar_id = query.get("id", [""])[0]
            kind = query.get("kind", ["video"])[0]
            media = avatar_media_path(avatar_id, kind)
            if media is None:
                self.send_error(404)
            elif kind == "poster":
                self.send_static(media)
            else:
                self.send_media(media)
        elif parsed.path == "/api/media":
            requested = urllib.parse.parse_qs(parsed.query).get("path", [""])[0]
            media = allowed_media_path(requested)
            if media is None:
                self.send_error(404)
            else:
                self.send_media(media)
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/avatar/upload":
                uploaded: Path | None = None
                try:
                    uploaded, original_name, fields = self.read_upload(
                        {".mp4", ".mov", ".avi", ".mkv"}, 8 * 1024 * 1024 * 1024
                    )
                    avatar = add_avatar(
                        uploaded, fields["name"] or Path(original_name).stem,
                        person_id=fields.get("personId") or "",
                    )
                    self.send_json({
                        "ok": True, "avatar": avatar,
                        "avatars": [public_avatar(item) for item in load_avatar_records()],
                    })
                finally:
                    if uploaded is not None:
                        uploaded.unlink(missing_ok=True)
                return
            if parsed.path == "/api/broll/upload":
                uploaded = None
                try:
                    uploaded, original_name, _ = self.read_upload(
                        {".mp4", ".mov", ".avi", ".mkv", ".webm"},
                        8 * 1024 * 1024 * 1024,
                    )
                    asset = add_broll_asset(uploaded, original_name)
                    self.send_json({"ok": True, "asset": asset})
                finally:
                    if uploaded is not None:
                        uploaded.unlink(missing_ok=True)
                return
            if parsed.path == "/api/voice/upload-local":
                uploaded = None
                try:
                    uploaded, original_name, fields = self.read_upload(
                        {".wav", ".mp3", ".m4a", ".flac", ".aac", ".mp4", ".mov", ".avi", ".mkv"},
                        2 * 1024 * 1024 * 1024,
                    )
                    voice = add_local_voice(
                        uploaded, fields["name"] or Path(original_name).stem, fields["promptText"],
                        fields.get("engine") or "v2",
                        person_id=fields.get("personId") or "",
                    )
                    schedule_voice_warmup(0.5)
                    self.send_json({
                        "ok": True, "voice": voice,
                        "voices": [public_voice(item) for item in load_voice_records()],
                    })
                finally:
                    if uploaded is not None:
                        uploaded.unlink(missing_ok=True)
                return
            if parsed.path == "/api/audio/upload":
                # 工作台"自己录音"模式：文件留在 temp/uploads，任务运行时转码进断点目录
                uploaded, original_name, _fields = self.read_upload(
                    {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"},
                    2 * 1024 * 1024 * 1024,
                )
                duration = media_duration(uploaded)
                if duration <= 0.5:
                    uploaded.unlink(missing_ok=True)
                    raise ValueError("无法读取这段录音，请换成 wav 或 mp3 格式。")
                self.send_json({
                    "ok": True, "path": str(uploaded), "name": original_name,
                    "duration": duration,
                })
                return
            if parsed.path == "/api/music/upload":
                uploaded = None
                try:
                    uploaded, original_name, fields = self.read_upload(
                        {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"},
                        2 * 1024 * 1024 * 1024,
                    )
                    music = add_music(uploaded, fields["name"] or Path(original_name).stem)
                    self.send_json({
                        "ok": True, "track": music,
                        "music": [public_music(item) for item in load_music_records()],
                    })
                finally:
                    if uploaded is not None:
                        uploaded.unlink(missing_ok=True)
                return
            payload = self.read_json()
            if parsed.path == "/api/pick":
                self.send_json({"ok": True, **pick_path(str(payload.get("kind") or "file"))})
            elif parsed.path == "/api/setup/install":
                start_setup([str(step) for step in (payload.get("steps") or [])])
                self.send_json({"ok": True})
            elif parsed.path == "/api/setup/cancel":
                SETUP_CANCEL.set()
                self.send_json({"ok": True})
            elif parsed.path == "/api/setup/config":
                # 写入 local-config.json 并热更新（显存阈值等无需重启即可生效）
                allowed_keys = {"gpuMinFreeMB", "modelBatchSize", "defaultOutput", "setupBundleDir"}
                updates = {
                    key: value for key, value in payload.items() if key in allowed_keys
                }
                if updates:
                    merged = dict(LOCAL_CONFIG)
                    merged.update(updates)
                    LOCAL_CONFIG_PATH.write_text(
                        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    LOCAL_CONFIG.clear()
                    LOCAL_CONFIG.update(merged)
                self.send_json({"ok": True, "config": dict(LOCAL_CONFIG)})
            elif parsed.path == "/api/output-folder/validate":
                folder = validate_output_folder(payload.get("path"))
                self.send_json({"ok": True, "path": str(folder)})
            elif parsed.path == "/api/avatar/import":
                selected = pick_path("video")
                if selected.get("cancelled"):
                    self.send_json({"ok": True, "cancelled": True})
                else:
                    avatar = add_avatar(
                        Path(str(selected["path"])),
                        person_id=str(payload.get("personId") or ""),
                    )
                    self.send_json({
                        "ok": True, "cancelled": False, "avatar": avatar,
                        "avatars": [public_avatar(item) for item in load_avatar_records()],
                    })
            elif parsed.path == "/api/avatar/delete":
                avatar_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", avatar_id):
                    raise ValueError("数字人形象编号无效。")
                assert_asset_not_used_by_queue("avatar", avatar_id)
                self.send_json({"ok": True, "avatars": delete_avatar(avatar_id)})
            elif parsed.path == "/api/avatar/rename":
                avatar_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", avatar_id):
                    raise ValueError("数字人形象编号无效。")
                self.send_json({
                    "ok": True,
                    "avatars": rename_avatar(avatar_id, str(payload.get("name") or "")),
                })
            elif parsed.path == "/api/broll/update":
                asset_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[A-Z0-9]{2,32}", asset_id):
                    raise ValueError("B-roll 素材编号无效。")
                asset = update_broll_asset(asset_id, payload)
                self.send_json({"ok": True, "asset": asset})
            elif parsed.path == "/api/broll/delete":
                asset_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[A-Z0-9]{2,32}", asset_id):
                    raise ValueError("B-roll 素材编号无效。")
                delete_broll_asset(asset_id)
                self.send_json({"ok": True})
            elif parsed.path == "/api/voice/import-local":
                supplied_path = str(payload.get("path") or "").strip()
                selected = {"cancelled": False, "path": supplied_path} if supplied_path else pick_path("voice")
                if selected.get("cancelled"):
                    self.send_json({"ok": True, "cancelled": True})
                else:
                    voice = add_local_voice(
                        Path(str(selected["path"])),
                        str(payload.get("name") or "").strip() or None,
                        str(payload.get("promptText") or "").strip(),
                        str(payload.get("engine") or "v2").strip(),
                        person_id=str(payload.get("personId") or "").strip(),
                    )
                    schedule_voice_warmup(0.5)
                    self.send_json({
                        "ok": True, "cancelled": False, "voice": voice,
                        "voices": [public_voice(item) for item in load_voice_records()],
                    })
            elif parsed.path == "/api/voice/add-elevenlabs":
                voice = add_elevenlabs_voice(str(payload.get("name") or ""), str(payload.get("voiceId") or ""))
                self.send_json({
                    "ok": True, "voice": voice,
                    "voices": [public_voice(item) for item in load_voice_records()],
                })
            elif parsed.path == "/api/voice/save-elevenlabs":
                voice = save_elevenlabs_voice(payload)
                self.send_json({
                    "ok": True, "voice": voice,
                    "voices": [public_voice(item) for item in load_voice_records()],
                })
            elif parsed.path == "/api/person/save":
                self.send_json({"ok": True, "persons": [public_person(item) for item in save_person(payload)]})
            elif parsed.path == "/api/person/delete":
                person_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", person_id):
                    raise ValueError("人物编号无效。")
                delete_person(person_id)
                self.send_json({"ok": True, "persons": [public_person(item) for item in load_persons()]})
            elif parsed.path == "/api/asset/set-person":
                set_asset_person(
                    str(payload.get("kind") or ""), str(payload.get("id") or ""),
                    normalize_person_id(payload.get("personId")),
                )
                self.send_json({"ok": True})
            elif parsed.path == "/api/elevenlabs/account/save":
                account, warning = save_elevenlabs_account(payload)
                self.send_json({
                    **elevenlabs_config_snapshot(),
                    "account": public_elevenlabs_account(account),
                    "warning": warning,
                })
            elif parsed.path == "/api/elevenlabs/account/sync":
                account_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", account_id):
                    raise ValueError("ElevenLabs 账号编号无效。")
                account = sync_elevenlabs_account(account_id)
                self.send_json({
                    **elevenlabs_config_snapshot(),
                    "account": public_elevenlabs_account(account),
                })
            elif parsed.path == "/api/elevenlabs/account/delete":
                account_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", account_id):
                    raise ValueError("ElevenLabs 账号编号无效。")
                delete_elevenlabs_account(account_id)
                self.send_json(elevenlabs_config_snapshot())
            elif parsed.path == "/api/voice/transcribe":
                voice_id = str(payload.get("voiceId") or payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", voice_id):
                    raise ValueError("声音编号无效。")
                self.send_json({"ok": True, "text": transcribe_voice_sample(voice_id)})
            elif parsed.path == "/api/voice/set-transcript":
                voice_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", voice_id):
                    raise ValueError("声音编号无效。")
                self.send_json({
                    "ok": True,
                    "voices": set_voice_transcript(voice_id, str(payload.get("promptText") or "")),
                })
            elif parsed.path == "/api/voice/delete":
                voice_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", voice_id):
                    raise ValueError("声音编号无效。")
                assert_asset_not_used_by_queue("voice", voice_id)
                self.send_json({"ok": True, "voices": delete_voice(voice_id)})
            elif parsed.path == "/api/voice/rename":
                voice_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", voice_id):
                    raise ValueError("声音编号无效。")
                self.send_json({
                    "ok": True,
                    "voices": rename_voice(voice_id, str(payload.get("name") or "")),
                })
            elif parsed.path == "/api/music/delete":
                music_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", music_id):
                    raise ValueError("音乐编号无效。")
                assert_asset_not_used_by_queue("music", music_id)
                self.send_json({"ok": True, "music": delete_music(music_id)})
            elif parsed.path == "/api/voice/clone":
                voice_id = str(payload.get("id") or "")
                if not re.fullmatch(r"[a-f0-9]{32}", voice_id):
                    raise ValueError("声音编号无效。")
                if snapshot_job("clone")["status"] == "running":
                    self.send_json({"ok": False, "error": "已有声音正在克隆。"}, 409)
                    return
                if (snapshot_job("main")["status"] == "running"
                        or snapshot_job("preview")["status"] == "running" or queue_is_busy()):
                    self.send_json({"ok": False, "error": "请等待当前声音或视频任务完成。"}, 409)
                    return
                record = next(
                    (item for item in load_voice_records()
                     if item["id"] == voice_id and item["provider"] == "local"),
                    None,
                )
                if record is None:
                    raise ValueError("没有找到要克隆的本地声音。")
                job_id = reset_job("clone")
                thread = threading.Thread(target=clone_voice_task, args=(voice_id,), daemon=True)
                thread.start()
                self.send_json({"ok": True, "jobId": job_id})
            elif parsed.path == "/api/preview":
                if (snapshot_job("preview")["status"] == "running"
                        or snapshot_job("clone")["status"] == "running" or queue_is_busy()):
                    self.send_json({"ok": False, "error": "试听正在生成。"}, 409)
                    return
                job_id = reset_job("preview")
                thread = threading.Thread(target=preview_task, args=(payload,), daemon=True)
                thread.start()
                self.send_json({"ok": True, "jobId": job_id})
            elif parsed.path == "/api/queue/start":
                queue = create_task_queue(payload)
                self.send_json(queue)
            elif parsed.path == "/api/queue/add":
                self.send_json(append_task_to_queue(payload))
            elif parsed.path == "/api/queue/action":
                self.send_json(apply_queue_action(payload))
            elif parsed.path == "/api/start":
                if (snapshot_job("main")["status"] == "running"
                        or snapshot_job("clone")["status"] == "running" or queue_is_busy()):
                    self.send_json({"ok": False, "error": "已有生成任务正在运行。"}, 409)
                    return
                validate_payload(payload, preview=False)
                MAIN_CANCEL.clear()
                job_id = reset_job("main")
                thread = threading.Thread(target=main_task, args=(payload,), daemon=True)
                thread.start()
                self.send_json({"ok": True, "jobId": job_id})
            elif parsed.path == "/api/open-result":
                job = snapshot_job("main")
                target = job.get("result") or job.get("outputDir") or str(DEFAULT_OUTPUT)
                path = open_output_folder(target)
                self.send_json({"ok": True, "path": str(path)})
            elif parsed.path == "/api/stop-models":
                stop_local_voice()
                self.send_json({"ok": True})
            else:
                self.send_error(404)
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"本地数字人已启动：http://{HOST}:{PORT}", flush=True)
    initialize_task_queue()
    # 上一个实例崩溃/被强杀可能留下声音服务孤儿进程占着显存内存，启动时先清掉
    cleanup_orphan_voice_processes()
    schedule_voice_warmup(1)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        stop_local_voice()
        server.server_close()


if __name__ == "__main__":
    main()
