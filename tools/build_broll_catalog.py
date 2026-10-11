from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return json.loads(completed.stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fraction(value: str | None) -> float:
    if not value or value in {"0/0", "N/A"}:
        return 0.0
    if "/" not in value:
        return float(value)
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator) if float(denominator) else 0.0


def probe(path: Path, ffprobe: Path) -> dict:
    payload = run_json(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate",
            "-of",
            "json",
            str(path),
        ]
    )
    video = next((item for item in payload.get("streams", []) if item.get("codec_type") == "video"), {})
    duration = float(payload.get("format", {}).get("duration") or 0)
    fps = fraction(video.get("avg_frame_rate")) or fraction(video.get("r_frame_rate"))
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    return {
        "durationSeconds": round(duration, 3),
        "width": width,
        "height": height,
        "fps": round(fps, 3),
        "codec": video.get("codec_name", ""),
        "portrait": bool(height > width),
        "aspectRatio": round(width / height, 4) if height else 0,
    }


def extract_frame(path: Path, target: Path, second: float, ffmpeg: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{max(0, second):.3f}",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-vf",
            "scale=240:426:force_original_aspect_ratio=decrease,pad=240:426:(ow-iw)/2:(oh-ih)/2:color=black",
            "-q:v",
            "3",
            str(target),
        ],
        check=True,
    )


def choose_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def write_contact_sheets(items: list[dict], root: Path, per_page: int = 6) -> list[str]:
    sheet_dir = root / "contact-sheets"
    sheet_dir.mkdir(parents=True, exist_ok=True)
    title_font = choose_font(26)
    body_font = choose_font(21)
    small_font = choose_font(18)
    paths: list[str] = []

    for page_index in range(math.ceil(len(items) / per_page)):
        page_items = items[page_index * per_page : (page_index + 1) * per_page]
        width = 1080
        header_h = 62
        row_h = 446
        canvas = Image.new("RGB", (width, header_h + row_h * len(page_items)), "#111827")
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (24, 14),
            f"B-Roll 初步盘点  第 {page_index + 1}/{math.ceil(len(items) / per_page)} 页",
            fill="#ffffff",
            font=title_font,
        )

        for row, item in enumerate(page_items):
            top = header_h + row * row_h
            draw.rectangle((0, top, width, top + row_h - 2), fill="#182233")
            for frame_index, frame_rel in enumerate(item["previewFrames"]):
                frame_path = root / frame_rel
                with Image.open(frame_path) as frame:
                    frame = frame.convert("RGB")
                    canvas.paste(frame, (20 + frame_index * 252, top + 10))

            text_x = 782
            draw.text((text_x, top + 12), item["id"], fill="#facc15", font=title_font)
            draw.text(
                (text_x, top + 56),
                truncate(item["sourceGroup"], 17),
                fill="#93c5fd",
                font=body_font,
            )
            draw.text(
                (text_x, top + 94),
                f"{item['durationSeconds']:.1f}s  {item['width']}×{item['height']}  {item['fps']:.1f}fps",
                fill="#e5e7eb",
                font=small_font,
            )
            name = truncate(item["filename"], 18)
            draw.multiline_text((text_x, top + 132), name, fill="#d1d5db", font=small_font, spacing=6)
            duplicate = item.get("duplicateOf")
            if duplicate:
                draw.text((text_x, top + 223), f"重复素材：{duplicate}", fill="#fca5a5", font=small_font)

        output = sheet_dir / f"broll-contact-{page_index + 1:02d}.jpg"
        canvas.save(output, quality=90)
        paths.append(str(output.relative_to(root)).replace("\\", "/"))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a non-destructive external B-roll catalog.")
    parser.add_argument("--ffmpeg", required=True, type=Path)
    parser.add_argument("--ffprobe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source", action="append", nargs=3, metavar=("PREFIX", "GROUP", "PATH"), required=True)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    thumbnail_root = args.output / "thumbnails"
    items: list[dict] = []

    for prefix, group, source_text in args.source:
        source = Path(source_text)
        files = sorted(
            [path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS],
            key=lambda path: path.name.lower(),
        )
        for position, path in enumerate(files, 1):
            asset_id = f"{prefix}{position:03d}"
            metadata = probe(path, args.ffprobe)
            digest = sha256(path)
            duration = metadata["durationSeconds"]
            moments = [duration * 0.15, duration * 0.5, duration * 0.85] if duration > 0 else [0, 0, 0]
            preview_frames: list[str] = []
            for frame_index, moment in enumerate(moments, 1):
                target = thumbnail_root / asset_id / f"{frame_index}.jpg"
                extract_frame(path, target, moment, args.ffmpeg)
                preview_frames.append(str(target.relative_to(args.output)).replace("\\", "/"))

            items.append(
                {
                    "id": asset_id,
                    "sourceGroup": group,
                    "sourceRoot": str(source),
                    "path": str(path),
                    "filename": path.name,
                    "extension": path.suffix.lower(),
                    "sizeBytes": path.stat().st_size,
                    "sha256": digest,
                    **metadata,
                    "previewFrames": preview_frames,
                    "duplicateOf": None,
                    "visualSummary": "",
                    "sceneTags": [],
                    "emotionTags": [],
                    "subjectTags": [],
                    "actionTags": [],
                    "themeTags": [],
                    "qualityFlags": [],
                    "usable": True,
                    "reviewStatus": "待人工初审",
                }
            )

    by_hash: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        by_hash[item["sha256"]].append(item)
    for duplicates in by_hash.values():
        for item in duplicates[1:]:
            item["duplicateOf"] = duplicates[0]["id"]
            item["qualityFlags"].append("内容重复")

    contact_sheets = write_contact_sheets(items, args.output)
    summary = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "catalogVersion": 1,
        "storageMode": "external-reference",
        "note": "原素材未移动、未改名、未删除；系统仅保存路径、预览图、技术信息和标签。",
        "assetCount": len(items),
        "uniqueAssetCount": sum(1 for item in items if not item["duplicateOf"]),
        "duplicateCount": sum(1 for item in items if item["duplicateOf"]),
        "portraitCount": sum(1 for item in items if item["portrait"]),
        "totalDurationSeconds": round(sum(item["durationSeconds"] for item in items), 3),
        "sourceGroups": {
            group: sum(1 for item in items if item["sourceGroup"] == group)
            for group in sorted({item["sourceGroup"] for item in items})
        },
        "contactSheets": contact_sheets,
        "assets": items,
    }
    with (args.output / "broll-index.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print(json.dumps({key: value for key, value in summary.items() if key != "assets"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
