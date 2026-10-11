from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


def encode_texts(tokenizer: Any, model: Any, texts: list[str], batch_size: int = 32) -> np.ndarray:
    vectors: list[np.ndarray] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt",
        )
        with torch.inference_mode():
            output = model(**inputs).last_hidden_state[:, 0]
            output = torch.nn.functional.normalize(output, p=2, dim=1)
        vectors.append(output.cpu().numpy().astype(np.float32, copy=False))
    return np.concatenate(vectors, axis=0) if vectors else np.empty((0, 0), dtype=np.float32)


def catalog_signature(assets: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for asset in assets:
        digest.update(str(asset.get("id") or "").encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(asset.get("searchText") or "").encode("utf-8"))
        digest.update(b"\0")
        for shot in asset.get("safeShots") or []:
            digest.update(
                f"{shot.get('safeStart')}:{shot.get('safeEnd')}".encode("ascii", errors="ignore")
            )
    return digest.hexdigest()


def load_or_build_asset_vectors(
    tokenizer: Any,
    model: Any,
    assets: list[dict[str, Any]],
    cache_path: Path,
) -> np.ndarray:
    signature = catalog_signature(assets)
    try:
        cached = np.load(cache_path, allow_pickle=False)
        cached_signature = str(cached["signature"].item())
        vectors = cached["vectors"]
        if cached_signature == signature and vectors.shape[0] == len(assets):
            return vectors.astype(np.float32, copy=False)
    except (OSError, ValueError, KeyError):
        pass

    descriptions = [
        str(asset.get("searchText") or asset.get("visualSummary") or asset.get("filename") or "")
        for asset in assets
    ]
    vectors = encode_texts(tokenizer, model, descriptions)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, signature=np.array(signature), vectors=vectors)
    return vectors


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: broll_matcher.py request.json")
    request_path = Path(sys.argv[1]).resolve()
    request = json.loads(request_path.read_text(encoding="utf-8"))
    catalog_path = Path(request["catalogPath"]).resolve()
    model_path = Path(request["modelPath"]).resolve()
    cache_path = Path(request.get("cachePath") or catalog_path.with_name("broll-embeddings.npz")).resolve()
    queries = [str(value).strip() for value in request.get("queries") or [] if str(value).strip()]
    top_k = max(1, min(20, int(request.get("topK") or 8)))
    require_safe_shots = bool(request.get("requireSafeShots", True))

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assets = []
    for item in catalog.get("assets") or []:
        if item.get("useMode") != "ready" or item.get("duplicateOf"):
            continue
        if not Path(str(item.get("path") or "")).is_file():
            continue
        if require_safe_shots and not item.get("safeShots"):
            continue
        assets.append(item)
    if not assets:
        print(json.dumps({"matches": [], "assetCount": 0}, ensure_ascii=False))
        return 0

    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    model = AutoModel.from_pretrained(str(model_path), local_files_only=True)
    model.eval()
    model.to("cpu")
    asset_vectors = load_or_build_asset_vectors(tokenizer, model, assets, cache_path)
    query_vectors = encode_texts(
        tokenizer,
        model,
        [QUERY_INSTRUCTION + query for query in queries],
        batch_size=16,
    )

    matches = []
    for query, query_vector in zip(queries, query_vectors):
        scores = asset_vectors @ query_vector
        ranked = np.argsort(-scores)[:top_k]
        items = []
        for index in ranked:
            asset = assets[int(index)]
            items.append({
                "id": asset.get("id"),
                "score": round(float(scores[int(index)]), 6),
                "visualSummary": asset.get("visualSummary") or "",
                "filename": asset.get("filename") or "",
            })
        matches.append({"query": query, "items": items})
    print(json.dumps({"matches": matches, "assetCount": len(assets)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
