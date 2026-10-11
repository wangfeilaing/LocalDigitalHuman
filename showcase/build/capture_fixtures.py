#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""抓取本机真实后端的 GET 接口响应，作为展示站假数据的原始输入（fixtures/）。

关键点：**只 import server 模块，绝不调用 main()**。
`server.py` 的 `main()` 里有 `schedule_voice_warmup(1)`，直接启动会在 1 秒后拉起本地声音服务、
吃掉 4-5GB 显存；而抓接口数据完全不需要它。所以这里自己起一个 ThreadingHTTPServer。

抓到的原始 JSON 含云端账号与 Voice ID 等敏感信息，`showcase/demo/fixtures/` 已加入 .gitignore，
真正对外的是由 build_showcase.py 脱敏后生成的 `demo/demo-data.js`。

用法：
  python capture_fixtures.py
"""
from __future__ import annotations

import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]      # showcase/build/ -> 工程根目录
OUT = PROJECT / "showcase" / "demo" / "fixtures"
PORT = 17861

# /api/status 与 /api/setup/steps 会探测 GPU 与组件（可能要几十秒到几分钟），超时给足
ENDPOINTS: dict[str, tuple[str, int]] = {
    "ping": ("/api/ping", 30),
    "status": ("/api/status", 900),
    "voices": ("/api/voices", 30),
    "avatars": ("/api/avatars", 30),
    "persons": ("/api/persons", 30),
    "broll": ("/api/broll", 60),
    "music": ("/api/music", 30),
    "queue": ("/api/queue", 30),
    "job-main": ("/api/job?kind=main", 30),
    "job-preview": ("/api/job?kind=preview", 30),
    "job-clone": ("/api/job?kind=clone", 30),
    "job-setup": ("/api/job?kind=setup", 30),
    "setup-steps": ("/api/setup/steps", 900),
    "elevenlabs-config": ("/api/elevenlabs/config", 60),
}


def main() -> None:
    sys.path.insert(0, str(PROJECT))
    import server  # noqa: E402  只导入，不执行 main()

    OUT.mkdir(parents=True, exist_ok=True)
    httpd = server.ThreadingHTTPServer(("127.0.0.1", PORT), server.AppHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    time.sleep(1.5)

    failures = 0
    try:
        for name, (endpoint, timeout) in ENDPOINTS.items():
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{PORT}{endpoint}", timeout=timeout
                ) as response:
                    raw = response.read().decode("utf-8")
                (OUT / f"{name}.json").write_text(
                    json.dumps(json.loads(raw), ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(f"  {name:20s} OK   {len(raw):>8} bytes", flush=True)
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"  {name:20s} FAIL {exc}", flush=True)
    finally:
        httpd.shutdown()

    print(f"\nfixtures -> {OUT}")
    if failures:
        print(f"有 {failures} 个接口抓取失败：先确认本机程序在运行（双击「启动本地数字人.vbs」）。")
        sys.exit(1)


if __name__ == "__main__":
    main()
