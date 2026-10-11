from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import AutoProcessor, CLIPModel


LABEL_GROUPS: dict[str, list[tuple[str, str]]] = {
    "primaryCategory": [
        ("亲子家庭", "a parent and child family scene"),
        ("亲密关系", "a romantic couple or intimate relationship scene"),
        ("心理健康", "a mental health emotion or psychological struggle scene"),
        ("个人成长", "a personal growth hope freedom or life journey scene"),
        ("睡眠健康", "a sleep bedtime insomnia or tiredness scene"),
        ("职场社会", "an office workplace career or professional scene"),
        ("城市生活", "an urban city daily life scene"),
        ("情绪氛围", "an atmospheric emotional cinematic scene"),
        ("成长教育", "a school education learning or childhood growth scene"),
        ("社会人文", "a social documentary or human life scene"),
        ("认知科学", "a brain neuroscience psychology or technology scene"),
    ],
    "sceneTags": [
        ("卧室", "a bedroom"), ("客厅", "a living room"), ("厨房", "a kitchen"),
        ("办公室", "an office"), ("城市街道", "a city street"), ("雨夜", "a rainy night"),
        ("海边", "a seaside"), ("山野", "mountains and nature"), ("公园", "a park"),
        ("课堂", "a classroom"), ("餐厅", "a restaurant"), ("车内", "inside a car"),
        ("乡村道路", "a countryside road"), ("暗场抽象", "a dark abstract stage"),
        ("日出", "a sunrise landscape"), ("日落", "a sunset landscape"),
    ],
    "emotionTags": [
        ("温暖", "warm comforting mood"), ("孤独", "lonely mood"),
        ("焦虑", "anxious mood"), ("希望", "hopeful mood"),
        ("浪漫", "romantic mood"), ("快乐", "happy joyful mood"),
        ("悲伤", "sad emotional mood"), ("平静", "calm peaceful mood"),
        ("压迫", "stressful oppressive mood"), ("治愈", "healing relaxing mood"),
        ("怀旧", "nostalgic mood"),
    ],
    "subjectTags": [
        ("女性", "a woman"), ("男性", "a man"), ("儿童", "a child"),
        ("老人夫妻", "an elderly couple"), ("家庭", "a family"), ("情侣", "a couple"),
        ("婴儿", "a baby"), ("手机", "a smartphone"), ("花卉", "flowers"),
        ("海洋", "the ocean"), ("城市", "a city"), ("大脑", "a human brain"),
    ],
    "actionTags": [
        ("行走", "walking"), ("交谈", "talking"), ("争吵", "arguing"),
        ("哭泣", "crying"), ("睡觉", "sleeping"), ("看手机", "using a smartphone"),
        ("拥抱", "hugging"), ("冥想", "meditating"), ("奔跑", "running"),
        ("工作", "working"), ("做饭", "cooking"), ("眺望", "looking into the distance"),
    ],
}


def as_tensor(features: Any) -> torch.Tensor:
    """transformers 新版的 get_image_features / get_text_features 返回
    ModelOutput 对象，旧版直接返回张量。两种都兼容。"""
    if torch.is_tensor(features):
        return features
    for attr in ("pooler_output", "image_embeds", "text_embeds"):
        value = getattr(features, attr, None)
        if torch.is_tensor(value):
            return value
    return features[0]


def rank_labels(
    model: Any,
    processor: Any,
    image_features: torch.Tensor,
    labels: list[tuple[str, str]],
    count: int,
) -> list[str]:
    prompts = [f"a video frame showing {prompt}" for _, prompt in labels]
    text_inputs = processor(text=prompts, return_tensors="pt", padding=True)
    with torch.inference_mode():
        text_features = as_tensor(model.get_text_features(**text_inputs))
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        scores = (image_features @ text_features.T).mean(dim=0)
    indices = torch.argsort(scores, descending=True)[:count].tolist()
    return [labels[index][0] for index in indices]


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: broll_classifier.py request.json")
    request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    model_path = Path(request["modelPath"]).resolve()
    images = [
        Image.open(path).convert("RGB")
        for path in request.get("imagePaths") or []
        if Path(path).is_file()
    ]
    if not images:
        raise RuntimeError("没有可用于识别的素材画面。")
    processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
    model = CLIPModel.from_pretrained(str(model_path), local_files_only=True)
    model.eval().to("cpu")
    image_inputs = processor(images=images, return_tensors="pt")
    with torch.inference_mode():
        image_features = as_tensor(model.get_image_features(**image_inputs))
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    primary = rank_labels(model, processor, image_features, LABEL_GROUPS["primaryCategory"], 1)[0]
    scenes = rank_labels(model, processor, image_features, LABEL_GROUPS["sceneTags"], 2)
    emotions = rank_labels(model, processor, image_features, LABEL_GROUPS["emotionTags"], 2)
    subjects = rank_labels(model, processor, image_features, LABEL_GROUPS["subjectTags"], 2)
    actions = rank_labels(model, processor, image_features, LABEL_GROUPS["actionTags"], 2)
    themes = list(dict.fromkeys([primary, *emotions, *subjects, *actions]))[:6]
    summary = f"{scenes[0]}中的{subjects[0]}，画面表现{actions[0]}与{emotions[0]}氛围"
    result = {
        "primaryCategory": primary,
        "visualSummary": summary,
        "sceneTags": scenes,
        "emotionTags": emotions,
        "subjectTags": subjects,
        "actionTags": actions,
        "themeTags": themes,
    }
    # Keep the worker output ASCII-only so Windows console code pages cannot
    # corrupt Chinese labels before the server reads the JSON response.
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
