from __future__ import annotations

import argparse
import json
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    args = parser.parse_args()

    started = time.time()
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        local_files_only=True,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    ).eval()
    load_seconds = time.time() - started

    prompt = (
        "请只输出一行JSON，不要解释。分析文案："
        "孩子深夜还在看手机，第二天上课没有精神。"
        "字段为theme、emotion、scene、keywords，每个值使用简短中文。"
    )
    messages = [
        {"role": "system", "content": "你是短视频文案素材匹配助手。"},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    infer_started = time.time()
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=96,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    result = tokenizer.decode(output[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True).strip()
    print(
        json.dumps(
            {
                "loadSeconds": round(load_seconds, 2),
                "inferenceSeconds": round(time.time() - infer_started, 2),
                "result": result,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
