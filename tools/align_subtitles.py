"""字幕强制对齐工具（FunASR 时间戳预测模型，CPU 运行，不占显存）。

用法：python tools/align_subtitles.py <request.json>
请求：{"ffmpeg": "ffmpeg.exe 路径（可选）", "pairs": [{"audio": "part_00001.mp3", "text": "该段音频对应的文案"}, ...]}
输出：stdout 最后一行 JSON
    {"ok": true, "segments": [{"charCount": 38, "timestamps": [[起ms, 止ms], ...]}, ...]}
模型：iic/speech_timestamp_prediction-v1-16k-offline —— 给定文本与音频做强制对齐，
timestamps 与「去除标点空白后的文本字符」一一对应；首次运行会从 ModelScope 下载模型。

注意：该时间戳模型只在短音频（约 15 秒以内）上可靠，长音频的尾部时间戳会被压缩
（99 秒音频实测尾部偏差超过 12 秒）。因此长音频做两遍分块对齐：先按能量静默点
切成 <= 12 秒的块、按块时长比例分配字符跑第一遍（结果已贴住真实时间轴），再把
块边界挪到第一遍结果里的真实停顿处跑第二遍，得到最终逐字时间戳。
"""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHUNK_TARGET_MS = 12000   # 每块目标时长（达到后找最近静默点切）
CHUNK_MAX_MS = 15000      # 找不到静默点时的硬切上限
SILENCE_MIN_MS = 120      # 至少这么久的低能量才算静默
CHUNK_SEARCH_MS = 3000    # 切点左右搜索静默点的范围


def clean_chars(text: str) -> str:
    return re.sub(r"[^\w一-鿿]+", "", text.lower())


def clean_index_map(text: str) -> list[int]:
    """净字符流中每个字符在原文里的下标。"""
    return [i for i, ch in enumerate(text) if re.match(r"[\w一-鿿]", ch.lower())]


def to_wav_16k(ffmpeg: str, audio: str, work_dir: Path) -> Path:
    """统一转成 16k 单声道 wav，避免 mp3 解码差异，也方便按样本切片。"""
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


def tp_align(model, audio_path: Path, text: str) -> list[list[float]]:
    result = model.generate(input=(str(audio_path), text), data_type=("sound", "text"))
    item = result[0] if isinstance(result, list) and result else {}
    return [[float(s), float(e)] for s, e in (item.get("timestamp") or [])]


def find_chunk_cuts(samples, sample_rate: int, duration_ms: float) -> list[float]:
    """按短时能量找静默点，把时间轴切成 <= CHUNK_MAX_MS 的小块，返回块边界（ms）。"""
    import numpy as np

    hop = int(sample_rate * 0.01)          # 10ms 一跳
    window = int(sample_rate * 0.02)       # 20ms 窗
    if len(samples) < window:
        return [0.0, duration_ms]
    frame_count = 1 + max(0, (len(samples) - window) // hop)
    rms = np.empty(frame_count, dtype=np.float64)
    for i in range(frame_count):
        frame = samples[i * hop: i * hop + window]
        rms[i] = math.sqrt(float(np.mean(frame * frame)) + 1e-12)
    noise_floor = float(np.percentile(rms, 20))
    threshold = max(noise_floor * 3.0, float(np.percentile(rms, 90)) * 0.02, 1e-5)
    silent = rms < threshold
    # 收集所有 >= SILENCE_MIN_MS 的静默区间中点（ms）
    min_frames = max(1, SILENCE_MIN_MS // 10)
    silence_mids: list[float] = []
    run_start: int | None = None
    for i, flag in enumerate(silent):
        if flag and run_start is None:
            run_start = i
        elif not flag and run_start is not None:
            if i - run_start >= min_frames:
                silence_mids.append((run_start + i) / 2 * 10.0)
            run_start = None
    if run_start is not None and frame_count - run_start >= min_frames:
        silence_mids.append((run_start + frame_count) / 2 * 10.0)

    bounds = [0.0]
    cursor = 0.0
    while duration_ms - cursor > CHUNK_MAX_MS:
        ideal = cursor + CHUNK_TARGET_MS
        candidates = [m for m in silence_mids
                      if ideal - CHUNK_SEARCH_MS <= m <= ideal + CHUNK_SEARCH_MS and m > cursor + 1000]
        if candidates:
            cut = min(candidates, key=lambda m: abs(m - ideal))
        else:
            cut = cursor + CHUNK_MAX_MS  # 没有静默点只能硬切（极少见）
        bounds.append(cut)
        cursor = cut
    bounds.append(duration_ms)
    return bounds


def align_chunks(model, samples, sample_rate: int, text: str, index_map: list[int],
                 spans: list[tuple[int, float, float]], work_dir: Path,
                 tag: str) -> list[list[float] | None]:
    """按 (起始净字符下标, 音频起点ms, 音频终点ms) 逐块对齐，返回全体净字符时间戳。"""
    import soundfile as sf

    char_count = len(index_map)
    output: list[list[float] | None] = [None] * char_count
    for k, (char_start, start_ms, end_ms) in enumerate(spans):
        char_end = spans[k + 1][0] if k + 1 < len(spans) else char_count
        count_k = char_end - char_start
        if count_k <= 0:
            continue
        slice_path = work_dir / f"align_{tag}_{k}.wav"
        sf.write(
            str(slice_path),
            samples[int(start_ms * sample_rate / 1000): int(end_ms * sample_rate / 1000)],
            sample_rate,
        )
        sub_text = text[index_map[char_start]: index_map[char_end - 1] + 1]
        try:
            chunk_ts = tp_align(model, slice_path, sub_text)
            if len(chunk_ts) != count_k:
                raise ValueError("块内字符数不一致")
            chunk_ts = [[s + start_ms, e + start_ms] for s, e in chunk_ts]
        except Exception:
            # 块内线性均分兜底，保证整块失败也不回退到全段估算
            span = max(100.0, end_ms - start_ms)
            step = span / count_k
            chunk_ts = [[start_ms + j * step, start_ms + (j + 1) * step] for j in range(count_k)]
        for j, stamp in enumerate(chunk_ts):
            output[char_start + j] = stamp
    return output


def align_long_audio(model, wav_path: Path, text: str, ffmpeg: str, work_dir: Path) -> list[list[float]]:
    """长音频两遍分块对齐：

    时间戳模型在超过约 15 秒的音频上会把尾部时间戳往前压缩（99 秒实测偏差 12 秒），
    所以先按能量静默点把音频切成 <= 12 秒的块，按块时长比例分配字符做第一遍对齐；
    第一遍结果已经贴在真实时间轴上，再用它把块边界挪到真实停顿处（停顿处切开，
    分块误差对字幕不可见），跑第二遍得到最终逐字时间戳。
    """
    import soundfile as sf

    samples, sample_rate = sf.read(str(wav_path), dtype="float32", always_2d=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    duration_ms = len(samples) / sample_rate * 1000.0
    clean_total = clean_chars(text)
    if not clean_total:
        raise ValueError("文案没有可对齐的有效字符。")

    if duration_ms <= CHUNK_MAX_MS:
        timestamps = tp_align(model, wav_path, text)
        if len(timestamps) != len(clean_total):
            raise ValueError(f"对齐字符数不一致：期望 {len(clean_total)}，实际 {len(timestamps)}")
        return timestamps

    index_map = clean_index_map(text)
    char_count = len(index_map)

    # ---- 第一遍：能量静默点切块 + 按块时长比例分配字符 ----
    bounds = find_chunk_cuts(samples, sample_rate, duration_ms)
    chunk_count = len(bounds) - 1
    total_span = sum(bounds[k + 1] - bounds[k] for k in range(chunk_count)) or 1.0
    spans: list[tuple[int, float, float]] = []
    char_cursor = 0
    acc = 0.0
    for k in range(chunk_count):
        acc += (bounds[k + 1] - bounds[k]) / total_span
        next_char = char_count if k == chunk_count - 1 else min(
            char_count, max(char_cursor, round(char_count * acc))
        )
        if next_char > char_cursor:
            spans.append((char_cursor, bounds[k], bounds[k + 1]))
            char_cursor = next_char
    first_pass = align_chunks(model, samples, sample_rate, text, index_map, spans, work_dir, "p1")
    if any(item is None for item in first_pass):
        raise ValueError("第一遍分块对齐不完整。")
    ts1 = [item for item in first_pass if item is not None]

    # ---- 第二遍：把每个块边界挪到第一遍结果里最近的真实停顿（字符间隙）处 ----
    refined: list[tuple[int, float, float]] = []
    prev_char = 0
    prev_time = 0.0
    for k in range(1, chunk_count):
        target = bounds[k]
        best: tuple[float, int, float] | None = None  # (gap, char_index, mid_time)
        for i in range(char_count - 1):
            gap = ts1[i + 1][0] - ts1[i][1]
            if gap < 150:
                continue
            mid = (ts1[i][1] + ts1[i + 1][0]) / 2
            if abs(mid - target) <= 4000 and (best is None or gap > best[0]):
                best = (gap, i + 1, mid)
        if best is not None:
            cut_char, cut_time = best[1], best[2]
        else:
            # 附近没有明显停顿：按第一遍时间直接二分
            import bisect
            starts = [s for s, _ in ts1]
            cut_char = bisect.bisect_right(starts, target)
            cut_time = target
        cut_char = max(prev_char + 1, min(char_count - 1, cut_char))
        refined.append((prev_char, prev_time, cut_time))
        prev_char, prev_time = cut_char, cut_time
    refined.append((prev_char, prev_time, duration_ms))
    second_pass = align_chunks(model, samples, sample_rate, text, index_map, refined, work_dir, "p2")
    if any(item is None for item in second_pass):
        raise ValueError("第二遍分块对齐不完整。")
    return [item for item in second_pass if item is not None]


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

        from funasr import AutoModel

        model = AutoModel(
            model="iic/speech_timestamp_prediction-v1-16k-offline",
            device="cpu",
            disable_update=True,
        )
        segments = []
        with tempfile.TemporaryDirectory(prefix="align_") as tmp:
            work_dir = Path(tmp)
            for pair in pairs:
                audio = str(pair.get("audio") or "")
                text = str(pair.get("text") or "").strip()
                if not audio or not text:
                    raise ValueError("对齐请求缺少音频或文本。")
                wav_path = to_wav_16k(ffmpeg, audio, work_dir)
                timestamps = align_long_audio(model, wav_path, text, ffmpeg, work_dir)
                expected = len(clean_chars(text))
                if len(timestamps) != expected:
                    raise ValueError(f"对齐字符数不一致：期望 {expected}，实际 {len(timestamps)}")
                segments.append({"charCount": expected, "timestamps": timestamps})
        print(json.dumps({"ok": True, "segments": segments}, ensure_ascii=True))
        return 0
    except Exception as exc:  # noqa: BLE001 - 任何失败都透传给工作台走兜底
        print(json.dumps({"ok": False, "error": str(exc)[:300]}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
