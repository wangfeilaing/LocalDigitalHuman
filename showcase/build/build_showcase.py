#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 LocalDigitalHuman 打包成一个可以在线访问的展示站（showcase/）。

产物：
  showcase/index.html            项目介绍落地页（手写，不由本脚本生成）
  showcase/demo/                 可点的纯静态 UI 演示（真实前端 + 假数据）
  showcase/demo/demo-data.js     从真实接口抓的 fixture 经脱敏/裁剪后生成
  showcase/demo/media/           演示用图片/短视频/音频（从真实素材转码）
  showcase/assets/               落地页素材（封面、成片片段、界面截图）

安全约定（重要）：
  * ElevenLabs 的 keyPreview、账号名、Voice ID 一律替换为演示值；
  * 真人姓名统一替换为「讲师A/B/C/D」；
  * 成片视频按用户授权保留，但只截取片段并压到 720p。

用法：
  python build_showcase.py            # 全流程
  python build_showcase.py media      # 只转码素材
  python build_showcase.py data       # 只生成 demo-data.js
  python build_showcase.py frontend   # 只同步前端并打补丁
  python build_showcase.py shots      # 只用 Edge 无头模式截界面图
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(r"D:\LocalDigitalHuman")
SHOWCASE = PROJECT / "showcase"
DEMO = SHOWCASE / "demo"
MEDIA = DEMO / "media"
ASSETS = SHOWCASE / "assets"
FIXTURES = DEMO / "fixtures"          # 原始抓包（不发布，见 .gitignore）
FFMPEG = PROJECT / "runtime" / "ffmpeg" / "bin" / "ffmpeg.exe"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

# 成片目录里挑两个片段：一个做首屏循环，一个做「完整成片示例」
OUTPUT_DIR = Path(r"D:\数字人视频输出")
HERO_SRC = OUTPUT_DIR / "看透了因果 就不会不甘心了.mp4"
RESULT_SRC = OUTPUT_DIR / "痛苦之所以太大 是因为心太小了.mp4"

# 演示用的形象（6 个）/ 声音（3 个）/ B-roll（10 条，取真实缩略图保证图文一致）
AVATARS = [
    ("fa346f6b6c5946dc9338b254e51172d9", "数字人顾问 01"),
    ("841ae75f4f8f4b86bbdb18e88750adbe", "数字人顾问 02"),
    ("bb6bd72de2b247fab91aa21c52278d31", "数字人顾问 03"),
    ("6f7d0090279b4d1d8cef4984e0938d2d", "数字人顾问 04"),
    ("fa35d2eb6ade42ba8e4ef58172471296", "数字人顾问 05"),
    ("e5d10c4c68ef4fd8b1d850564549ea27", "数字人顾问 06"),
]
VOICES = [
    ("07b87ebf318c485481dd73d60c91822d", "沉稳男声 · 讲师A", "local", "v2"),
    ("1df8d19d76a4480cab980358050b40a5", "亲切女声 · 讲师B", "local", "voxcpm"),
    ("3bf0090343e84a48830653a0399d20bc", "磁性男声 · 讲师C", "local", "v2"),
]
MUSIC_IDS = [
    ("f7325372ad1144d68fbd8e9f183c6201", "氛围垫乐 01", 117.6),
    ("3603f208ac0d4703a360d809b90ea8dd", "氛围垫乐 02", 112.9),
    ("dd2e661b9e5144598e704927f1fb1c24", "氛围垫乐 03", 63.8),
    ("2ab8fcfebea2446d956bd1c57caf317a", "氛围垫乐 04", 96.4),
]

PERSON_MAP = {
    "3e9d57f9fa324957aa14b7cbce6763dc": "讲师A",
    "33f1b2689b3a47b5a67c4e2c6aec431c": "讲师B",
    "3487df315ae44908b1f415ba2acbc134": "讲师C",
    "7aa4ec64905b4d02aa4b87c0d8a07034": "讲师D",
}

# 脱敏用：以这些词结尾的字段若是外部 URL / 本机绝对路径，一律丢弃
SENSITIVE_KEY_RE = re.compile(r"(?:url|path|dir)$", re.IGNORECASE)
EXTERNAL_REF_RE = re.compile(r"^(?:https?://|[A-Za-z]:[\\/]|\\\\)", re.IGNORECASE)


def log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def run(cmd: list[str], quiet: bool = True) -> None:
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.PIPE if quiet else None,
    )
    if result.returncode != 0:
        detail = (result.stderr or b"").decode("utf-8", "ignore")[-800:]
        raise RuntimeError(f"命令失败({result.returncode}): {' '.join(cmd[:6])}...\n{detail}")


def ffmpeg(*args: str) -> None:
    run([str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", *args])


# ---------------------------------------------------------------------------
# 1. 素材转码
# ---------------------------------------------------------------------------
def build_media() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("[1/4] 转码演示素材")

    # 形象封面 + 形象预览短片（只用前两个真实视频，其余共用，控制体积）
    for index, (avatar_id, _name) in enumerate(AVATARS, start=1):
        src_poster = PROJECT / "data" / "avatars" / f"{avatar_id}.jpg"
        if src_poster.exists():
            ffmpeg("-i", str(src_poster), "-vf", "scale=480:-2", str(MEDIA / f"avatar-{index:02d}.jpg"))
        src_video = PROJECT / "data" / "avatars" / f"{avatar_id}.mp4"
        target = 1 if index <= 2 else (2 if index <= 4 else 3)
        if index <= 6 and not (MEDIA / f"avatar-{target:02d}.mp4").exists() and src_video.exists():
            ffmpeg("-ss", "20", "-t", "5", "-i", str(src_video),
                   "-vf", "scale=480:-2", "-an",
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
                   "-movflags", "+faststart", str(MEDIA / f"avatar-{target:02d}.mp4"))
    for index in range(1, 7):
        fallback = MEDIA / f"avatar-{min(index, 3):02d}.jpg"
        target = MEDIA / f"avatar-{index:02d}.jpg"
        if not target.exists() and fallback.exists():
            shutil.copyfile(fallback, target)
    log(f"形象封面 {len(list(MEDIA.glob('avatar-*.jpg')))} 张 / 预览片 {len(list(MEDIA.glob('avatar-*.mp4')))} 段")

    # B-roll 缩略图
    broll_count = 0
    for index in range(1, 11):
        src = PROJECT / "data" / "broll" / "thumbnails" / f"A{index:03d}" / "1.jpg"
        if src.exists():
            ffmpeg("-i", str(src), "-vf", "scale=480:-2", str(MEDIA / f"broll-{index:02d}.jpg"))
            broll_count += 1
    log(f"B-roll 缩略图 {broll_count} 张")
    # B-roll 预览片：素材原视频不在工程内（uploads 为空），用成片片段顶替并标注为演示素材
    if RESULT_SRC.exists():
        for index, start in enumerate(("8", "16"), start=1):
            ffmpeg("-ss", start, "-t", "4", "-i", str(RESULT_SRC),
                   "-vf", "scale=-2:540", "-an",
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
                   "-movflags", "+faststart", str(MEDIA / f"broll-clip-{index:02d}.mp4"))
    log("B-roll 预览片 2 段")

    # 声音样本试听（真实克隆音色，已获授权随成片公开）
    voice_count = 0
    for index, (voice_id, _name, _provider, _engine) in enumerate(VOICES, start=1):
        src = PROJECT / "data" / "voices" / f"{voice_id}_clone.wav"
        if not src.exists():
            src = PROJECT / "data" / "voices" / f"{voice_id}.wav"
        if src.exists():
            ffmpeg("-i", str(src), "-t", "12", "-vn", "-ac", "1", "-b:a", "96k",
                   str(MEDIA / f"voice-{index:02d}.mp3"))
            voice_count += 1
    log(f"声音试听 {voice_count} 段")

    # 背景音乐：真实曲目有版权风险，用合成氛围垫乐顶替
    for index in range(1, 5):
        base = 196 + index * 24
        ffmpeg("-f", "lavfi",
               "-i", f"sine=frequency={base}:duration=24",
               "-f", "lavfi", "-i", f"sine=frequency={base * 1.5}:duration=24",
               "-filter_complex",
               "[0:a][1:a]amix=inputs=2,tremolo=f=0.4:d=0.6,volume=0.18,afade=t=in:d=2,afade=t=out:st=22:d=2[a]",
               "-map", "[a]", "-ac", "1", "-b:a", "96k", str(MEDIA / f"music-{index:02d}.mp3"))
    log("氛围垫乐 4 段（合成占位，规避版权）")

    # 成片片段：首屏 20 秒 / 完整示例 45 秒，都压到 720p
    # 带宽预算：轻量服务器默认只有 3M 带宽（≈375 KB/s），所以首屏的每一个字节都要省。
    if HERO_SRC.exists():
        # 首屏是 muted 自动播放，原片那条 103 kb/s 音轨纯属浪费（省下约 260KB）。
        # 注意：HERO_SRC 是 4K 源片，必须显式 scale 到 720 长边——第一版误以为源就是
        # 406x720（那其实是上一次的产物），去掉 scale 后编出了 12MB 的 4K 首屏。
        ffmpeg("-ss", "65", "-t", "20", "-i", str(HERO_SRC),
               "-vf", "scale=-2:720", "-an",
               "-c:v", "libx264", "-preset", "slower", "-crf", "29",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(ASSETS / "hero.mp4"))
        ffmpeg("-ss", "3", "-i", str(ASSETS / "hero.mp4"), "-frames:v", "1",
               str(ASSETS / "hero-poster.jpg"))
        log(f"首屏循环片 hero.mp4（20s/720 长边/无音轨，{(ASSETS / 'hero.mp4').stat().st_size / 1024:.0f} KB）")
    if RESULT_SRC.exists():
        # 只产出 result.mp4（演示层「生成结果」播放的就是它），
        # 落地页的成片示例由它复制成 assets/full-demo.mp4 —— 不再单独编一份 MEDIA/full-demo.mp4，
        # 那份没有任何地方引用，纯属 1.9MB 死重量。
        ffmpeg("-ss", "30", "-t", "45", "-i", str(RESULT_SRC),
               "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "slower", "-crf", "31",
               "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", str(MEDIA / "result.mp4"))
        shutil.copyfile(MEDIA / "result.mp4", ASSETS / "full-demo.mp4")
        ffmpeg("-ss", "5", "-i", str(ASSETS / "full-demo.mp4"), "-frames:v", "1",
               str(MEDIA / "result-cover.jpg"))
        ffmpeg("-ss", "5", "-i", str(ASSETS / "full-demo.mp4"), "-frames:v", "1",
               str(ASSETS / "full-demo-poster.jpg"))
        log(f"成片示例 result.mp4 -> assets/full-demo.mp4（720p/45s，{(ASSETS / 'full-demo.mp4').stat().st_size / 1024:.0f} KB）")

    # 应用图标：项目根目录那张是 1.1MB 的 1024px 原图，展示站只需要 256px（导航 28px 显示 + 头像兜底）
    icon = PROJECT / "assets" / "app-icon.png"
    if icon.exists():
        ffmpeg("-i", str(icon), "-vf", "scale=256:256", str(ASSETS / "app-icon.png"))
        log(f"应用图标压缩到 256px（{(ASSETS / 'app-icon.png').stat().st_size / 1024:.0f} KB）")
    total = sum(f.stat().st_size for f in MEDIA.rglob("*") if f.is_file())
    total += sum(f.stat().st_size for f in ASSETS.rglob("*") if f.is_file())
    log(f"素材总体积 {total / 1024 / 1024:.1f} MB")

    # ---- 带宽预算闸门 ----------------------------------------------------
    # 国内轻量服务器默认 3M 带宽 ≈ 375 KB/s。首屏三件套一旦超标，面试官就要盯着转圈，
    # 所以这里做成硬失败，而不是打个日志放过去（12MB 的首屏视频就是这么被抓出来的）。
    first_paint = [ASSETS / "hero.mp4", ASSETS / "app-icon.png"]
    budget = sum(f.stat().st_size for f in first_paint if f.exists())
    log(f"首屏关键资源 {budget / 1024:.0f} KB（3M 带宽约 {budget / 1024 / 375:.1f} 秒）")
    if budget > 2.5 * 1024 * 1024:
        raise RuntimeError(
            f"首屏资源超预算：{budget / 1024 / 1024:.1f} MB > 2.5 MB。"
            "请检查 hero.mp4 是否忘了 scale 到 720 长边（4K 源片直接编码会到 10MB 以上）。"
        )
    oversized = [f for f in list(ASSETS.rglob("*")) + list(MEDIA.rglob("*"))
                 if f.is_file() and f.stat().st_size > 3 * 1024 * 1024]
    for big in oversized:
        log(f"⚠ 单文件偏大：{big.relative_to(SHOWCASE)} {big.stat().st_size / 1024 / 1024:.1f} MB"
            "（EdgeOne Pages 单文件上限 25MiB，3M 带宽下也会明显拖慢加载）")


# ---------------------------------------------------------------------------
# 2. 假数据（从真实抓包脱敏 + 裁剪）
# ---------------------------------------------------------------------------
def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def deep_sanitize(node):
    """递归兜底脱敏：不管抓包里哪个层级冒出敏感字段，都在这里被替换掉。

    靠逐字段白名单很容易漏（第一版漏了 ElevenLabs 同步下来的声音列表，第二版漏了
    嵌套在别处的 previewUrl），所以这里按「键名 + 值的形态」双维度兜底：
      * voiceId / keyPreview 直接换成演示值；
      * 任何以 Url / Path / Dir 结尾、且值是外部 URL 或本机绝对路径的字段一律丢弃
        （ElevenLabs 的预览链接里嵌着 voice id，base64 载荷里还有 workspace_id）；
      * 字符串里的真人姓名统一替换成别名。
    演示站自己的素材用的是相对路径（media/xxx.mp4），不受影响。
    """
    if isinstance(node, dict):
        cleaned = {}
        for key, value in node.items():
            if key == "voiceId":
                cleaned[key] = "DEMO_VOICE_ID_NOT_REAL" if value else value
                continue
            if key == "keyPreview":
                cleaned[key] = "demo"
                continue
            if (SENSITIVE_KEY_RE.search(key) and isinstance(value, str)
                    and EXTERNAL_REF_RE.match(value)):
                continue
            cleaned[key] = deep_sanitize(value)
        return cleaned
    if isinstance(node, list):
        return [deep_sanitize(item) for item in node]
    if isinstance(node, str):
        for real, alias in PERSON_MAP.items():
            node = node.replace(real, alias)
        return node
    return node


def build_data() -> None:
    print("[2/4] 生成 demo-data.js")
    data: dict[str, object] = {}

    # --- 设备/组件状态：保留真实硬件信息（这就是项目卖点），路径换成演示值
    status = load_fixture("status")
    status["defaultOutput"] = r"D:\数字人视频输出"
    data["status"] = status
    data["setup-steps"] = load_fixture("setup-steps")

    # --- 人物分组：真人姓名脱敏
    data["persons"] = {"ok": True, "persons": [
        {"id": pid, "name": name, "createdAt": "2026-08-13 20:18:54"}
        for pid, name in PERSON_MAP.items()
    ]}

    # --- 声音模型
    voices = []
    for index, (voice_id, name, provider, engine) in enumerate(VOICES, start=1):
        person_id = list(PERSON_MAP)[index - 1]
        voices.append({
            "id": voice_id,
            "name": name,
            "provider": provider,
            "personId": person_id,
            "createdAt": "2026-08-11 13:11:22",
            "samplePath": f"D:\\LocalDigitalHuman\\data\\voices\\{voice_id}.wav",
            "sampleUrl": f"media/voice-{index:02d}.mp3",
            "previewUrl": f"media/voice-{index:02d}.mp3",
            "promptText": "",
            "status": "ready",
            "clonedAt": "2026-08-11 13:11:31",
            "cloneError": "",
            "engine": engine,
            "engineName": "IndexTTS-2 · 本地免费" if engine == "v2" else "VoxCPM2 · 本地免费",
        })
    # 再补一条 ElevenLabs 云端声音，展示双引擎路由（ID 全部为演示值）
    voices.append({
        "id": "demo-eleven-voice-0001",
        "name": "云端克隆 · 讲师D",
        "provider": "elevenlabs",
        "personId": list(PERSON_MAP)[3],
        "createdAt": "2026-08-12 23:14:32",
        "voiceId": "DEMO_VOICE_ID_NOT_REAL",
        "accountId": "demo-eleven-account",
        "accountName": "ElevenLabs 演示账号",
        "accountStatus": "ready",
        "status": "ready",
        "category": "professional",
        "engine": "elevenlabs",
        "engineName": "ElevenLabs 云端",
        "sampleUrl": "media/voice-01.mp3",
        "previewUrl": "media/voice-01.mp3",
        "promptText": "",
        "cloneError": "",
    })
    data["voices"] = {"ok": True, "voices": voices}

    # --- 数字人形象
    avatars = []
    for index, (avatar_id, name) in enumerate(AVATARS, start=1):
        person_id = list(PERSON_MAP)[(index - 1) % len(PERSON_MAP)]
        avatars.append({
            "id": avatar_id,
            "name": name,
            "videoPath": f"D:\\LocalDigitalHuman\\data\\avatars\\{avatar_id}.mp4",
            "posterUrl": f"media/avatar-{min(index, 3):02d}.jpg",
            "videoUrl": f"media/avatar-{min((index + 1) // 2, 3):02d}.mp4",
            "personId": person_id,
            "createdAt": f"2026-08-11 {16 + index % 3:02d}:05:33",
            "duration": 200 + index * 37.4,
            "usageCount": 3 + index,
            "lastStartOffset": 60.0 + index * 20,
        })
    data["avatars"] = {"ok": True, "avatars": avatars}

    # --- B-roll 素材库：取真实条目保证「摘要 ↔ 缩略图」对得上，文件名换成摘要
    real_broll = load_fixture("broll").get("assets", [])
    broll = []
    for index, asset in enumerate(real_broll[:10], start=1):
        summary = (asset.get("summary") or "").strip() or f"演示素材 {index:02d}"
        broll.append({
            "id": f"B{index:03d}",
            "name": f"{summary}.mp4",
            "summary": summary,
            "category": asset.get("category") or "情绪氛围",
            "sourceGroup": "演示素材库",
            "tags": (asset.get("tags") or [])[:8],
            "duration": asset.get("duration") or 6.0,
            "width": asset.get("width") or 576,
            "height": asset.get("height") or 1024,
            "useMode": "ready",
            "usable": True,
            "uploaded": False,
            "posterUrl": f"media/broll-{index:02d}.jpg",
            "videoUrl": f"media/broll-clip-{1 + index % 2:02d}.mp4",
            "personId": "",
            "createdAt": "2026-08-11",
        })
    data["broll"] = {"ok": True, "assets": broll}

    # --- 背景音乐
    data["music"] = {"ok": True, "music": [
        {"id": mid, "name": name, "duration": duration, "audioUrl": f"media/music-{index:02d}.mp3",
         "createdAt": "2026-08-11 18:10:18"}
        for index, (mid, name, duration) in enumerate(MUSIC_IDS, start=1)
    ]}

    # --- ElevenLabs 账号：密钥尾号/账号名/Voice ID 全部替换，额度也换成演示值
    eleven = load_fixture("elevenlabs-config")
    demo_quota = [(200000, 46000), (100000, 81000), (200000, 71500)]
    for acc_index, account in enumerate(eleven.get("accounts", []), start=1):
        account["name"] = f"ElevenLabs 演示账号 {acc_index}"
        account["hasKey"] = True
        account["keyPreview"] = "demo"
        account["id"] = f"demo-eleven-account-{acc_index}"
        subscription = account.get("subscription") or {}
        limit, used = demo_quota[(acc_index - 1) % len(demo_quota)]
        subscription["characterLimit"] = limit
        subscription["characterCount"] = used
        subscription["usagePercent"] = round(used / limit * 100, 1)
        account["subscription"] = subscription
    # 同步下来的云端声音列表也带真人姓名，一并脱敏并裁到 6 条
    eleven = deep_sanitize(eleven)
    cloud_voices = eleven.get("voices")
    if isinstance(cloud_voices, list):
        # 白名单重建：凡是 *Url / *Path 一律不带（ElevenLabs 的预览链接里嵌着真实 voice id，
        # 链接的 base64 载荷里还会带 workspace_id，属于账号信息）
        cloud_keep = {"id", "name", "voiceId", "category", "labels", "description",
                      "accountId", "accountName", "gender", "accent", "age", "useCase"}
        rebuilt = []
        for index, voice in enumerate(cloud_voices[:6], start=1):
            item = {key: voice[key] for key in cloud_keep if key in voice}
            item["voiceId"] = "DEMO_VOICE_ID_NOT_REAL"
            item["name"] = f"云端声音 {index:02d}"
            item["accountId"] = "demo-eleven-account-1"
            item["accountName"] = "ElevenLabs 演示账号 1"
            rebuilt.append(item)
        eleven["voices"] = rebuilt
    data["elevenlabs-config"] = eleven

    # --- 队列：造 4 条不同状态的任务，把队列 UI 的每种状态都演出来
    now = int(time.time())
    base_items = [
        {"id": "demo-q1", "position": 1, "title": "众生皆苦 苦在把一场体验当成了占有",
         "characters": 412, "status": "done", "progress": 100, "stage": "已完成",
         "avatarIndex": 0, "voiceName": "沉稳男声 · 讲师A", "quality": "v2", "resolution": "4k",
         "createdAt": now - 9000, "startedAt": now - 8700, "finishedAt": now - 8100,
         "resolutionSeconds": 3720, "brollEnabled": True, "musicId": MUSIC_IDS[0][0]},
        {"id": "demo-q2", "position": 2, "title": "不再渴望被爱 才真正拥有了爱",
         "characters": 368, "status": "done", "progress": 100, "stage": "已完成",
         "avatarIndex": 1, "voiceName": "亲切女声 · 讲师B", "quality": "v2", "resolution": "2k",
         "createdAt": now - 7800, "startedAt": now - 7600, "finishedAt": now - 7000,
         "resolutionSeconds": 2640, "brollEnabled": True, "musicId": MUSIC_IDS[1][0]},
        {"id": "demo-q3", "position": 3, "title": "身体比脑子更清楚 谁在消耗你",
         "characters": 296, "status": "error", "progress": 42, "stage": "口型同步",
         "error": "显存不足：需要 6500MB 可用，当前 5120MB（演示数据）",
         "avatarIndex": 2, "voiceName": "磁性男声 · 讲师C", "quality": "v2", "resolution": "4k",
         "createdAt": now - 3600, "startedAt": now - 3400, "finishedAt": now - 3000,
         "resolutionSeconds": 1900, "brollEnabled": False, "musicId": ""},
        {"id": "demo-q4", "position": 4, "title": "越是顺 越要管住自己的嘴",
         "characters": 240, "status": "cancelled", "progress": 18, "stage": "分段合成语音",
         "avatarIndex": 0, "voiceName": "沉稳男声 · 讲师A", "quality": "v2", "resolution": "2k",
         "createdAt": now - 1200, "startedAt": now - 1100, "finishedAt": now - 900,
         "resolutionSeconds": 640, "brollEnabled": True, "musicId": MUSIC_IDS[2][0]},
    ]
    items = []
    for index, raw in enumerate(base_items):
        avatar = avatars[raw["avatarIndex"]]
        items.append({
            "id": raw["id"],
            "position": raw["position"],
            "title": raw["title"],
            "characters": raw["characters"],
            "avatarId": avatar["id"],
            "avatarName": avatar["name"],
            "voiceName": raw["voiceName"],
            "voiceAccountName": "",
            "elevenGenerationMode": "",
            "elevenGenerationModeName": "",
            "avatarPosterUrl": avatar["posterUrl"],
            "status": raw["status"],
            "progress": raw["progress"],
            "stage": raw["stage"],
            "result": "media/result.mp4" if raw["status"] == "done" else None,
            "cover": "media/result-cover.jpg" if raw["status"] == "done" else None,
            "error": raw.get("error"),
            "createdAt": raw["createdAt"],
            "startedAt": raw["startedAt"],
            "finishedAt": raw["finishedAt"],
            "quality": raw["quality"],
            "resolution": raw["resolution"],
            "brollEnabled": raw["brollEnabled"],
            "musicId": raw["musicId"],
        })
    data["queue"] = {
        "ok": True, "status": "done", "paused": False, "total": 4,
        "pending": 0, "pausedItems": 0, "completed": 2, "failed": 1,
        "activePosition": 0, "overallProgress": 65.0, "items": items,
    }
    data["job-main"] = {"kind": "main", "id": None, "status": "idle", "progress": 0,
                        "stage": "", "message": "", "error": None, "result": None,
                        "cover": None, "audio": None, "outputDir": None,
                        "segmentsTotal": 0, "segmentsDone": 0, "startedAt": None,
                        "elapsedSeconds": 0, "estimatedSeconds": None, "log": []}
    data["job-preview"] = {"kind": "preview", "status": "idle", "progress": 0, "audio": None, "error": None}
    data["job-clone"] = {"kind": "clone", "status": "idle", "progress": 0, "error": None}
    data["job-setup"] = {"kind": "setup", "status": "idle", "progress": 0, "stage": "", "log": []}
    data["ping"] = {"ok": True, "app": "LocalDigitalHuman · 在线演示"}

    # 兜底：整个数据结构再过一遍递归脱敏
    data = deep_sanitize(data)

    payload = json.dumps(data, ensure_ascii=False, indent=1)
    header = (
        "// 本文件由 showcase/build/build_showcase.py 自动生成，请勿手改。\n"
        "// 数据来源：真实后端接口抓包 -> 脱敏（密钥尾号/真人姓名/云端 Voice ID 全部替换）-> 裁剪。\n"
        "// 生成时间：" + time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        "window.__DEMO_DATA__ = " + payload + ";\n"
    )
    (DEMO / "demo-data.js").write_text(header, encoding="utf-8")

    # 构建期自检：宁可构建失败，也不能把真人姓名或云端账号信息发到公网
    leaks = [name for name in PERSON_MAP if name in header]
    leaks += re.findall(r'"voiceId":\s*"(?!DEMO_VOICE_ID_NOT_REAL)[A-Za-z0-9_-]{12,}"', header)
    leaks += re.findall(r'"keyPreview":\s*"(?![dD]emo")[0-9a-f]{2,}"', header)
    leaks += re.findall(r'"[A-Za-z]*Url":\s*"https?://[^"]{20,}"', header)
    leaks += re.findall(r'"[A-Za-z]*(?:Path|Dir)":\s*"[A-Za-z]:[\\/]', header)
    if leaks:
        raise RuntimeError(f"脱敏自检失败，仍存在敏感内容：{sorted(set(leaks))}")
    log(f"demo-data.js 生成完毕（{len(header.encode('utf-8')) / 1024:.0f} KB，{len(data)} 个接口，脱敏自检通过）")


# ---------------------------------------------------------------------------
# 3. 同步前端 + 打补丁（让绝对路径变成相对路径、注入演示脚本）
# ---------------------------------------------------------------------------
def build_frontend() -> None:
    print("[3/4] 同步前端并注入演示脚本")
    # 真人姓名脱敏：不止接口数据，静态 HTML/JS 里也写死了默认人名
    # 公开仓库不含真实姓名；本机版本在这里维护同样的映射。
    name_map: dict[str, str] = {}

    def sanitize(text: str) -> str:
        for real, alias in name_map.items():
            text = text.replace(real, alias)
        return text

    for name in ("app.js", "styles.css", "ui-fx.js"):
        content = (PROJECT / name).read_text(encoding="utf-8")
        if name.endswith(".js"):
            content = sanitize(content)
            leaked = [real for real in name_map if real in content]
            if leaked:
                log(f"⚠ {name} 仍含未脱敏姓名：{leaked}")
        (DEMO / name).write_text(content, encoding="utf-8")
        log(f"复制 {name}")

    html = (PROJECT / "index.html").read_text(encoding="utf-8")
    # 演示站常部署在子路径下（如 OSS 的 /showcase/、EdgeOne 的根），绝对路径会 404
    html = html.replace('href="/styles.css', 'href="./styles.css')
    html = html.replace('src="/ui-fx.js', 'src="./ui-fx.js')
    html = html.replace('src="/app.js', 'src="./app.js')
    html = html.replace('href="/assets/app-icon.png', 'href="../assets/app-icon.png')
    html = html.replace('src="/assets/app-icon.png', 'src="../assets/app-icon.png')
    html = html.replace("<title>本地数字人工作台</title>", "<title>本地数字人工作台 · 在线演示</title>")
    # 工作台原本是桌面端工具界面（Edge app 模式），在手机上按 device-width 渲染会横向溢出、
    # 按钮被裁掉。演示页固定按 1280 桌面宽渲染，手机用户看到的是完整界面缩放图。
    html = html.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="viewport" content="width=1280">',
    )
    html = sanitize(html)
    leaked_html = [real for real in name_map if real in html]
    if leaked_html:
        log(f"⚠ index.html 仍含未脱敏姓名：{leaked_html}")
    # 演示脚本必须在 app.js 之前执行：它负责接管 fetch，让整套 UI 用假数据跑起来
    html = html.replace(
        '<script src="./ui-fx.js',
        '<script src="./demo-data.js"></script>\n  <script src="./demo-api.js"></script>\n  <script src="./ui-fx.js',
    )
    (DEMO / "index.html").write_text(html, encoding="utf-8")
    log("index.html 已改写为相对路径、脱敏并注入 demo-data.js / demo-api.js")


# ---------------------------------------------------------------------------
# 4. Edge 无头截图（拿真实界面当落地页配图）
# ---------------------------------------------------------------------------
SHOTS = [
    ("shot-workbench", "step=1", "1600,1000", 9000),
    ("shot-voices", "step=2", "1600,1000", 9000),
    ("shot-avatars", "step=3", "1600,1000", 9000),
    ("shot-broll", "step=5", "1600,1000", 9000),
    ("shot-workbench-tall", "step=1&scroll=bottom", "1600,2200", 9000),
    # 用 ?freeze 冻结出确定性的「生成中 / 已完成」状态：
    # 虚拟时间会加速计时器，而全新 profile 首次加载又慢，靠真实跑一遍根本稳不住"跑到一半"那一帧。
    # 真实跑完整条流水线的端到端自检另外用 ?autostart=1&debug=1 人工执行（见 README）。
    ("shot-generating", "step=1&freeze=46&scroll=bottom", "1600,2200", 9000),
    ("shot-result", "step=1&freeze=done&scroll=bottom", "1600,2200", 9000),
]


def patch_shot_refs() -> None:
    """截图转成 JPEG 后，把落地页与文档里的引用一起改掉（幂等）。

    产出仍是 1600px 宽的界面图，但 PNG -> JPEG 能省约 85% 体积：
    7 张加起来从 5.3MB 降到 0.8MB，对 3M 带宽的轻量服务器是决定性的。

    注意：这里必须按截图名单拼名字，不能去 glob `shot-*.png`——
    转换完成后 PNG 已经被删掉了，glob 会得到空集合（第一版就踩了这个坑）。
    """
    targets = [SHOWCASE / "index.html", SHOWCASE / "README.md", PROJECT / "README.md"]
    changed = 0
    for target in targets:
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        original = text
        for name, *_ in SHOTS:
            if (ASSETS / f"{name}.jpg").exists():
                text = text.replace(f"{name}.png", f"{name}.jpg")
        if text != original:
            target.write_text(text, encoding="utf-8")
            changed += 1
            log(f"{target.relative_to(PROJECT)} 的截图引用已更新为 .jpg")
    if not changed:
        log("截图引用无需更新（已是 .jpg）")


def build_shots() -> None:
    print("[4/4] Edge 无头模式截界面图")
    if not EDGE.exists():
        log(f"未找到 Edge，跳过：{EDGE}")
        return
    import http.server
    import socketserver
    import threading

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *args, directory=str(SHOWCASE), **kwargs
    )
    with socketserver.TCPServer(("127.0.0.1", 8099), handler) as httpd:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        time.sleep(0.8)
        profile = Path(r"D:\deepseek\tmp\edge-shot-profile")
        # 每次都用全新 profile：复用旧 profile 会带上上一轮的 localStorage 草稿，
        # restoreDraft() 恢复出的选择可能让前端校验失败，导致 ?autostart 自检静默不生效。
        if profile.exists():
            shutil.rmtree(profile, ignore_errors=True)
        profile.mkdir(parents=True, exist_ok=True)
        for name, query, size, budget in SHOTS:
            url = f"http://127.0.0.1:8099/demo/?{query}&chrome=0"
            png = ASSETS / f"{name}.png"
            jpg = ASSETS / f"{name}.jpg"
            run([
                str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--no-first-run", "--disable-extensions",
                f"--user-data-dir={profile}",
                f"--window-size={size}", f"--virtual-time-budget={budget}",
                f"--screenshot={png}", url,
            ])
            if not png.exists():
                log(f"{name} 截图失败")
                continue
            # Edge 只能输出 PNG，这里立刻转 JPEG（宽 1400 足够 2x 屏显示）并删掉 PNG
            ffmpeg("-i", str(png), "-vf", "scale=1400:-2", "-q:v", "3", str(jpg))
            png.unlink()
            log(f"{name}.jpg {jpg.stat().st_size / 1024:.0f} KB")
        httpd.shutdown()
    patch_shot_refs()


PHASES = {
    "media": build_media,
    "data": build_data,
    "frontend": build_frontend,
    "shots": build_shots,
}


def main() -> None:
    selected = sys.argv[1:] or list(PHASES)
    for phase in selected:
        if phase not in PHASES:
            print(f"未知阶段：{phase}（可选：{', '.join(PHASES)}）")
            return
        PHASES[phase]()


if __name__ == "__main__":
    main()
