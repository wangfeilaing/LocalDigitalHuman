#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把一个服务器上要放的所有项目组装成一个站点目录（门户 + 各项目子目录）。

为什么需要它：一个轻量服务器上通常不只放一个项目。把「门户页 + 各项目路径」
都做成配置驱动（site.json），以后新增项目只要加一段配置再重新部署，
不用改服务器配置、也不用记 nginx 语法。

产物（都在 showcase/build/ 下，已在 .gitignore 里）：
  _stage/                 可以直接整体上传的站点目录
  │  ├─ index.html        门户页（由 site.json 生成）
  │  ├─ digital-human/    各项目按 slug 分子目录
  │  └─ ...
  _site.nginx.conf        配套的 nginx 配置（静态 root + 需要后端的项目反代）

用法：
  python build_site.py
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
SHOWCASE = BUILD_DIR.parent                     # showcase/
PROJECT = SHOWCASE.parent                       # 工程根目录
SITE_CONFIG = BUILD_DIR / "site.json"
# 暂存目录必须放在**所有被拷贝的项目目录之外**：它曾经被放在 showcase/build/ 下，
# 而 digital-human 项目的源目录正是 showcase/，于是 copytree 自己套自己，
# 一直递归到 Windows 路径超长才报错。放在工程根目录下并加忽略规则双重保险。
STAGE = PROJECT / "_site"
NGINX_CONF = PROJECT / "_site.nginx.conf"
COPY_IGNORE = shutil.ignore_patterns(
    "_site", "_stage", "__pycache__", ".git", "node_modules", "*.pyc", "fixtures",
)

# 门户页样式与展示站保持同一套深色 + 冷色光晕语言（自包含，不引用任何外部资源）
PORTAL_CSS = """
*{box-sizing:border-box}
body{margin:0;background:#080b14;color:#e8eefc;
  font:16px/1.7 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
  min-height:100vh}
body::before{content:"";position:fixed;inset:0;pointer-events:none;
  background:
    radial-gradient(60% 45% at 18% 0%,rgba(96,140,255,.20),transparent 70%),
    radial-gradient(50% 40% at 88% 12%,rgba(150,110,255,.16),transparent 72%),
    radial-gradient(70% 50% at 50% 110%,rgba(60,110,220,.14),transparent 70%)}
.wrap{position:relative;max-width:1060px;margin:0 auto;padding:clamp(48px,9vh,110px) clamp(20px,5vw,40px) 80px}
.eyebrow{display:inline-flex;align-items:center;gap:9px;padding:6px 14px;border-radius:999px;
  border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.04);
  font-size:12.5px;letter-spacing:.1em;color:#9fb2d4}
.eyebrow i{width:7px;height:7px;border-radius:50%;background:#5ee6a8;box-shadow:0 0 12px #5ee6a8}
h1{margin:22px 0 0;font-size:clamp(30px,5.2vw,52px);line-height:1.14;letter-spacing:-.02em;font-weight:680}
.lede{margin:18px 0 0;max-width:640px;color:#a9b8d4;font-size:clamp(15px,1.5vw,17.5px)}
.grid{margin-top:52px;display:grid;gap:22px}
.card{position:relative;display:block;padding:26px 26px 24px;border-radius:18px;
  border:1px solid rgba(255,255,255,.09);background:linear-gradient(180deg,rgba(20,26,44,.92),rgba(13,17,30,.92));
  text-decoration:none;color:inherit;transition:border-color .18s,transform .18s,box-shadow .18s}
a.card:hover{border-color:rgba(126,170,255,.5);transform:translateY(-2px);
  box-shadow:0 24px 60px rgba(40,80,180,.24)}
.card h2{margin:0;font-size:21px;font-weight:640;letter-spacing:-.01em}
.card .tag{margin:8px 0 0;color:#8fa6cc;font-size:14.5px}
.card p{margin:14px 0 0;color:#9fb0cc;font-size:14.6px}
.tags{margin:16px 0 0;display:flex;flex-wrap:wrap;gap:8px}
.tags span{padding:4px 10px;border-radius:999px;font-size:12.4px;color:#a9c2e8;
  border:1px solid rgba(126,170,255,.26);background:rgba(126,170,255,.08)}
.go{margin-top:18px;display:inline-flex;align-items:center;gap:8px;color:#7fb4ff;font-size:14.6px}
.card.off{opacity:.55;cursor:default}
.card.off .go{color:#7d8ba6}
footer{position:relative;margin-top:56px;padding-top:22px;border-top:1px solid rgba(255,255,255,.08);
  color:#7d8ba6;font-size:13.4px}
@media (max-width:640px){.card{padding:22px 18px}.wrap{padding-top:56px}}
"""

PORTAL_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <span class="eyebrow"><i></i>作品集 · 在线可访问</span>
  <h1>{title}</h1>
  <p class="lede">{subtitle}</p>
  <div class="grid">
{cards}
  </div>
  <footer>
    共 {total} 个项目，{online} 个可在线访问 · 全部为本地推理产物，页面为静态托管<br>
    在线演示均为脱敏数据；真实生成能力需要 Windows + NVIDIA 显卡在本机运行
  </footer>
</div>
</body>
</html>
"""

CARD_ONLINE = """    <a class="card" href="./{slug}/">
      <h2>{title}</h2>
      <p class="tag">{tagline}</p>
      <p>{description}</p>
      <div class="tags">{tags}</div>
      <span class="go">进入项目 →</span>
    </a>"""

CARD_OFFLINE = """    <div class="card off">
      <h2>{title}</h2>
      <p class="tag">{tagline}</p>
      <p>{description}</p>
      <div class="tags">{tags}</div>
      <span class="go">即将上线</span>
    </div>"""


def load_config() -> dict:
    return json.loads(SITE_CONFIG.read_text(encoding="utf-8"))


def build_stage(config: dict) -> tuple[int, int, float]:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    total = online = 0
    size = 0.0
    cards: list[str] = []
    for project in config.get("projects", []):
        # visible 未显式声明时跟随 enabled；隐藏的项目完全不渲染。
        # 这条是给"还没准备好、文案里还带着 TODO"的项目用的——
        # 面试官不能看到任何 TODO 或"待补充"。
        visible = project.get("visible")
        if visible is None:
            visible = bool(project.get("enabled"))
        if not visible:
            print(f"  [隐藏] {project.get('slug')}（visible=false，门户页不显示）")
            continue

        total += 1
        tags = "".join(f"<span>{html.escape(str(tag))}</span>" for tag in project.get("tags", []))
        fields = {
            "slug": project.get("slug", ""),
            "title": html.escape(project.get("title", "")),
            "tagline": html.escape(project.get("tagline", "")),
            "description": html.escape(project.get("description", "")),
            "tags": tags,
        }
        enabled = bool(project.get("enabled"))
        source_dir = Path(project.get("dir", "")) if project.get("dir") else None

        if enabled and source_dir and source_dir.is_dir():
            # 防御：源目录里若包含暂存目录，copytree 会无限递归直到路径超长
            if STAGE == source_dir or STAGE.is_relative_to(source_dir):
                raise SystemExit(
                    f"拒绝拷贝：暂存目录 {STAGE} 位于项目源目录 {source_dir} 内部，"
                    "会无限递归。请把 STAGE 挪到所有项目目录之外。"
                )
            target = STAGE / project["slug"]
            shutil.copytree(source_dir, target, ignore=COPY_IGNORE)
            if not (target / "index.html").exists():
                print(f"  [警告] {project['slug']} 目录里没有 index.html，路径访问会 404")
            project_size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
            size += project_size / 1024 / 1024
            online += 1
            cards.append(CARD_ONLINE.format(**fields))
            print(f"  [OK]   {project['slug']:<18} <- {source_dir}  ({project_size / 1024 / 1024:.1f} MB)")
        elif enabled:
            print(f"  [跳过] {project['slug']}：dir 不存在或为空 -> {project.get('dir')!r}")
            cards.append(CARD_OFFLINE.format(**fields))
        else:
            cards.append(CARD_OFFLINE.format(**fields))
            print(f"  [未启用] {project['slug']}（门户页显示为「即将上线」）")

    if not cards:
        cards.append(
            '    <div class="card off"><h2>内容准备中</h2>'
            '<p class="tag">还没有可展示的项目</p>'
            '<p>在 showcase/build/site.json 里把某个项目的 enabled 改成 true 即可上线。</p></div>'
        )

    portal = PORTAL_HTML.format(
        title=html.escape(config.get("title", "作品集")),
        subtitle=html.escape(config.get("subtitle", "")),
        css=PORTAL_CSS,
        cards="\n".join(cards),
        total=total,
        online=online,
    )
    (STAGE / "index.html").write_text(portal, encoding="utf-8")
    size += (STAGE / "index.html").stat().st_size / 1024 / 1024
    return total, online, size


def build_web_config(config: dict) -> str:
    """生成服务器端 nginx 配置。

    为什么是 nginx 而不是 Caddy（实测换过一次）：
      * Caddy 不在 Ubuntu 官方源里；它的官方 apt 源（Cloudsmith）从这台服务器访问
        返回 402 Payment Required，而且会留下一条坏源，让之后每次 apt-get update 都失败；
      * 改用官方静态二进制，curl 在没有超时参数时又会卡在"等连接关闭"上（实测挂死）；
      * nginx 在 Ubuntu / Debian / RHEL 官方源里都有（走云厂商内网镜像，秒级且有签名），
        而本站的需求只是「静态文件 + 需要后端的项目反代」，nginx 完全够用。
    这里用 Python 生成而不是在 PowerShell 里拼字符串：ps1 的 here-string 会被 bash 的
    $(...) 与 PowerShell 的插值互相干扰。
    """
    port = config.get("port", 8080)
    root = config.get("remoteRoot", "/var/www/site")
    lines = [
        "# 由 showcase/build/build_site.py 依据 site.json 自动生成，请勿手改。",
        "server {",
        f"    listen {port} default_server;",
        f"    listen [::]:{port} default_server;",
        "    server_name _;",
        "",
        f"    root {root};",
        "    index index.html;",
        "",
        "    gzip on;",
        "    gzip_comp_level 5;",
        "    gzip_min_length 1024;",
        "    gzip_types text/plain text/css application/javascript application/json image/svg+xml;",
    ]
    for project in config.get("projects", []):
        if not (project.get("enabled") and project.get("kind") == "proxy"):
            continue
        backend = project.get("backendPort")
        lines += [
            "",
            f"    # {project.get('title', project['slug'])}：反代到本机 {backend}",
            f"    location /{project['slug']}/ {{",
            f"        proxy_pass http://127.0.0.1:{backend}/;",
            "        proxy_set_header Host $host;",
            "        proxy_set_header X-Real-IP $remote_addr;",
            "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            "        proxy_set_header X-Forwarded-Proto $scheme;",
            "    }",
        ]
    lines += [
        "",
        "    location / {",
        "        try_files $uri $uri/ =404;",
        "    }",
        "}",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    if not SITE_CONFIG.exists():
        raise SystemExit(f"缺少站点配置：{SITE_CONFIG}")
    config = load_config()
    print("组装站点：")
    total, online, size = build_stage(config)
    NGINX_CONF.write_text(build_web_config(config), encoding="utf-8")

    print(f"\n门户页：{STAGE / 'index.html'}")
    print(f"站点目录：{STAGE}（{total} 个项目，{online} 个已上线，{size:.1f} MB）")
    print(f"nginx 配置：{NGINX_CONF}")
    print("\n本地预览：")
    print(f'  python -m http.server {config.get("port", 8080)} --directory "{STAGE}"')


if __name__ == "__main__":
    main()
