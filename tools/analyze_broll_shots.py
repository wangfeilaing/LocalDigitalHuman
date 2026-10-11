from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ANALYSIS_VERSION = 1
SCENE_THRESHOLD = 0.20
BOUNDARY_MARGIN = 0.18
MIN_CLIP_SECONDS = 4.0
MAX_CLIP_SECONDS = 7.0


def detect_boundaries(ffmpeg: Path, video: Path, duration: float) -> list[float]:
    command = [
        str(ffmpeg), "-hide_banner", "-loglevel", "info", "-i", str(video),
        "-an", "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo", "-f", "null", "-",
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=max(120, int(duration * 8)),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or "镜头检测失败")[-600:])
    detected = [float(value) for value in re.findall(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)", completed.stderr)]
    boundaries = [0.0]
    for value in sorted(detected):
        value = max(0.0, min(duration, value))
        if value - boundaries[-1] >= 0.45 and duration - value >= 0.20:
            boundaries.append(value)
    if duration - boundaries[-1] < 0.20 and len(boundaries) > 1:
        boundaries.pop()
    boundaries.append(duration)
    return boundaries


def build_safe_shots(boundaries: list[float]) -> list[dict[str, Any]]:
    shots = []
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        safe_start = start + BOUNDARY_MARGIN
        safe_end = end - BOUNDARY_MARGIN
        safe_duration = safe_end - safe_start
        if safe_duration + 1e-6 < MIN_CLIP_SECONDS:
            continue
        shots.append({
            "shot": index,
            "sceneStart": round(start, 3),
            "sceneEnd": round(end, 3),
            "safeStart": round(safe_start, 3),
            "safeEnd": round(safe_end, 3),
            "safeDuration": round(safe_duration, 3),
            "maxClipSeconds": round(min(MAX_CLIP_SECONDS, safe_duration), 3),
        })
    return shots


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    catalog_path = Path(args.catalog).resolve()
    ffmpeg = Path(args.ffmpeg).resolve()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    ready = [item for item in catalog.get("assets") or [] if item.get("useMode") == "ready"]
    eligible = 0
    failed = 0
    for position, item in enumerate(ready, start=1):
        existing = item.get("sceneAnalysis") or {}
        if not args.force and existing.get("version") == ANALYSIS_VERSION and "safeShots" in item:
            eligible += int(bool(item.get("safeShots")))
            print(f"[{position}/{len(ready)}] {item.get('id')} 已分析")
            continue
        path = Path(str(item.get("path") or ""))
        duration = max(0.0, float(item.get("durationSeconds") or 0.0))
        try:
            if not path.is_file() or duration <= 0:
                raise RuntimeError("素材文件不存在或时长无效")
            boundaries = detect_boundaries(ffmpeg, path, duration)
            safe_shots = build_safe_shots(boundaries)
            item["sceneAnalysis"] = {
                "version": ANALYSIS_VERSION,
                "threshold": SCENE_THRESHOLD,
                "boundaryMarginSeconds": BOUNDARY_MARGIN,
                "boundaryCount": max(0, len(boundaries) - 2),
                "boundaries": [round(value, 3) for value in boundaries],
            }
            item["safeShots"] = safe_shots
            item["brollEligible"] = bool(safe_shots)
            item.pop("sceneAnalysisError", None)
            eligible += int(bool(safe_shots))
            print(
                f"[{position}/{len(ready)}] {item.get('id')} "
                f"镜头 {len(boundaries) - 1} 个，可用区间 {len(safe_shots)} 个"
            )
        except Exception as exc:
            failed += 1
            item["safeShots"] = []
            item["brollEligible"] = False
            item["sceneAnalysisError"] = str(exc)
            print(f"[{position}/{len(ready)}] {item.get('id')} 失败：{exc}")
    catalog["shotCatalogVersion"] = ANALYSIS_VERSION
    catalog["shotAnalyzedAt"] = datetime.now().isoformat(timespec="seconds")
    catalog["shotRules"] = {
        "sceneThreshold": SCENE_THRESHOLD,
        "boundaryMarginSeconds": BOUNDARY_MARGIN,
        "clipSeconds": [MIN_CLIP_SECONDS, MAX_CLIP_SECONDS],
        "fadeSeconds": [0.5, 1.0],
    }
    catalog["brollEligibleCount"] = eligible
    catalog["sceneAnalysisFailureCount"] = failed
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"完成：{eligible}/{len(ready)} 条素材具备安全截取区间，失败 {failed} 条。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
