"""Apply safe local performance settings in every packaged-model subprocess."""

from __future__ import annotations

import os
from pathlib import Path


def apply_runtime_settings() -> None:
    if os.environ.get("LOCAL_DH_FACE_CACHE") not in {"0", "1"}:
        return
    try:
        from y_utils.config import GlobalConfig
    except Exception:
        return

    cache_enabled = int(os.environ.get("LOCAL_DH_FACE_CACHE", "0"))
    cache_dir = os.environ.get("LOCAL_DH_FACE_CACHE_DIR", "./face_cache")
    original_init = GlobalConfig.__init__

    if not getattr(original_init, "_local_dh_optimized", False):
        def optimized_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.batch_size = int(os.environ.get("BATCH_SIZE", "6"))
            self.parallel_face_detect = int(os.environ.get("PARALLEL_FACE_DETECT", "1"))
            self.parallel_threads = int(os.environ.get("PARALLEL_THREADS", "4"))
            self.face_cache_enable = cache_enabled
            self.face_cache_dir = cache_dir
            self.face_cache_show_log = 0

        optimized_init._local_dh_optimized = True
        GlobalConfig.__init__ = optimized_init

    instance = getattr(GlobalConfig, "_instance", None)
    if instance is not None:
        instance.batch_size = int(os.environ.get("BATCH_SIZE", "6"))
        instance.parallel_face_detect = int(os.environ.get("PARALLEL_FACE_DETECT", "1"))
        instance.parallel_threads = int(os.environ.get("PARALLEL_THREADS", "4"))
        instance.face_cache_enable = cache_enabled
        instance.face_cache_dir = cache_dir
        instance.face_cache_show_log = 0

    Path(cache_dir).mkdir(parents=True, exist_ok=True)


apply_runtime_settings()
