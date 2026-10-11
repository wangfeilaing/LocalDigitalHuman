# showcase —— 在线展示站

面试官点开链接能看到的东西都在这里：**项目介绍页 + 可点的界面演示 + 成片视频**。
整个目录是**纯静态**的（HTML/CSS/原生 JS + 媒体文件），不需要后端、不需要构建工具链，丢到任何静态服务器上就能跑。

## 目录结构

```
showcase/
├─ index.html                项目介绍页（手写，单文件，无外部依赖）
├─ 预览展示站.cmd             双击本地预览本站（起服务 + 开浏览器）
├─ deploy.cmd                一键发布到服务器（见 DEPLOY.md）
├─ DEPLOY.md                 怎么发到公网（含免备案方案对比）——要看这个
├─ assets/                   介绍页素材：成片片段、界面截图、应用图标
│   ├─ hero.mp4 / hero-poster.jpg        9:16 竖版成片片段（首屏，无音轨）
│   ├─ full-demo.mp4 / *-poster.jpg      完整成片示例（720p/45s）
│   ├─ shot-workbench.jpg                工作台
│   ├─ shot-workbench-tall.jpg           任务队列（整夜排队、失败续跑）
│   ├─ shot-generating.jpg               生成中（阶段 + 进度）
│   ├─ shot-result.jpg                   生成完成
│   ├─ shot-voices.jpg / -avatars.jpg / -broll.jpg
├─ demo/                     可点的界面演示：真实前端 + 脱敏假数据
│   ├─ index.html            从项目根目录复制并打补丁（相对路径、脱敏、注入演示脚本）
│   ├─ app.js / styles.css / ui-fx.js    同上，是副本不是软链接
│   ├─ demo-data.js          「接口响应」假数据（构建脚本生成，勿手改）
│   ├─ demo-api.js           演示层：接管 fetch、重写媒体地址、模拟生成流水线
│   ├─ media/                演示用图片/短视频/音频（从真实素材转码）
│   └─ fixtures/             真实接口原始抓包（**不入库**，仅作构建输入）
└─ build/
    ├─ build_showcase.py     四阶段构建：media / data / frontend / shots
    ├─ site.json             ★ 站点总配置：门户标题、端口、项目清单（加项目改这里）
    ├─ build_site.py         读 site.json，组装整站到仓库根目录的 _site/
    ├─ capture_fixtures.py   从本机真实后端抓接口响应（fixtures/ 的来源）
    ├─ deploy_to_server.ps1  发布/体检脚本（纯 ASCII，由 deploy.cmd 调用）
    └─ export_public_repo.py 导出可安全公开的 GitHub 副本（脱敏 + 自检）
```

## 多项目站点（门户 + 各项目）

这台服务器上可以放多个项目，组织方式是「门户页 + 每个项目一个子目录」：

```
_site/                        构建产物（在仓库根目录，已 gitignore）
├─ index.html                 门户页：面试官第一眼看到这个
├─ digital-human/             本项目（从 showcase/ 复制而来）
└─ <slug>/                    以后新增的项目
```

- **唯一配置源是 `build/site.json`**：门户标题、端口、项目清单、每个项目的源目录与形态。
  加项目就是加一段 JSON。两个开关：`enabled`（是否上传该项目的文件）、
  `visible`（是否在门户页露出，默认跟随 `enabled`）。
  —— `enabled: true, visible: false` 适合"已上线但不想在门户列出来"；
  `visible: false` 是给**还没准备好、文案里还带 TODO 的项目**用的：
  面试官不该在门户页看到"待补充"这种字样（这一条是实测发现门户页把自己的 TODO 显示出来后才加的）。
- **`build_site.py` 负责组装**：拷贝各项目目录、生成门户页、生成配套的 `_site.nginx.conf`
  （静态 root；`"kind": "proxy"` 的项目会生成 `handle_path ... reverse_proxy` 反代块）。
  nginx 配置用 Python 生成而不是在 ps1 里拼字符串——ps1 的 here-string 会被 bash 的 `$(...)`
  和 PowerShell 插值互相干扰，第一版就因此在本地解析失败过。
- **本地预览整站**：双击仓库根目录的 `预览作品集.cmd`，或
  `python -m http.server 8080 --directory D:\LocalDigitalHuman\_site`。

> 踩坑记录：暂存目录最初放在 `showcase/build/_stage`，而 digital-human 项目的源目录正是
> `showcase/`，于是 `copytree` 自己套自己一直递归到 Windows 路径超长。现在暂存目录放在
> 仓库根目录的 `_site/`（所有项目目录之外），并在拷贝时忽略 `_site`/`_stage`/`fixtures`，
> 另加一条"暂存目录不得位于源目录内部"的防御性断言。

## 一键构建

```powershell
# 全流程：转码素材 -> 生成假数据 -> 同步前端 -> Edge 无头截图
& 'C:\Users\w1227\AppData\Local\Programs\Python\Python310\python.exe' `
  D:\LocalDigitalHuman\showcase\build\build_showcase.py

# 只跑某一阶段
... build_showcase.py data frontend     # 改了接口数据或前端之后
... build_showcase.py shots             # 只想重截界面图
```

各阶段做什么：

| 阶段 | 作用 | 数据来源 |
|---|---|---|
| `media` | 把真实素材转成网页素材（720p 片段、480px 缩略图、声音试听、合成垫乐） | `data/avatars`、`data/voices`、`D:\数字人视频输出` |
| `data` | 生成 `demo/demo-data.js`：真实接口抓包 → 脱敏 → 裁剪 | `demo/fixtures/*.json` |
| `frontend` | 复制 `index.html`/`app.js`/`styles.css`/`ui-fx.js`，改成相对路径、姓名脱敏、注入演示脚本 | 项目根目录 |
| `shots` | 用 Edge 无头模式截真实界面图（含自动跑一条生成任务） | 本机 Edge + 本地静态服务 |

### 抓真实接口数据（`fixtures/` 的来源）

```powershell
& 'C:\Users\w1227\AppData\Local\Programs\Python\Python310\python.exe' `
  D:\LocalDigitalHuman\showcase\build\capture_fixtures.py
```

思路是**只 import `server` 模块、不调用 `main()`**——因为 `main()` 里有 `schedule_voice_warmup(1)`，
直接启动会拉起声音服务吃掉 4-5GB 显存。抓完的原始 JSON 含云端账号信息，所以 `fixtures/` 已加入 `.gitignore`。

## 本地预览

```powershell
python -m http.server 8080 --directory D:\LocalDigitalHuman\showcase
# 介绍页  http://127.0.0.1:8080/
# 界面演示 http://127.0.0.1:8080/demo/
```

也可以直接双击本目录下的 **`预览展示站.cmd`**（自动起服务并打开浏览器）。

不要用 `file://` 直接打开：演示层用 `fetch` 接管请求，某些浏览器在 `file://` 下会拦截。

## 演示层是怎么工作的（`demo-api.js`）

`app.js` 是经典脚本，所有请求都走全局 `fetch` 和 `uploadApi`。演示层在 `app.js` **之前**加载，做三件事：

1. **接管 `fetch`**：命中 `/api/*` 就返回 `demo-data.js` 里的假数据，不联网。
2. **重写媒体地址**：`patchProperty` 改写 `HTMLMediaElement.src` / `HTMLImageElement.src` / `HTMLVideoElement.poster`，
   把 `/api/avatar-media?id=...`、`/api/media?path=...` 之类的地址映射到 `demo/media/` 下的静态文件。
3. **模拟生成流水线**：点「添加并自动开始」后按真实阶段推进（分段合成语音 → 字幕逐字对齐 → 口型同步 →
   B-roll 匹配 → 导出），进度、阶段名、耗时实时回传，跑完弹出成片并自动接队列里的下一条，
   还原真实 worker「整夜排队」的行为。

URL 参数（自检与截图用）：

| 参数 | 作用 |
|---|---|
| `?step=2` | 直接打开指定面板（1 工作台 / 2 声音模型 / 3 数字人形象 / 5 B-roll） |
| `?freeze=46` / `?freeze=done` | 冻结出确定性的「生成中 / 已完成」状态（截图与自检用，不依赖计时器） |
| `?autostart=1` | 自动填文案并点真实的「添加并自动开始」按钮，端到端跑完整条流水线 |
| `?scroll=bottom` | 滚到面板底部（截队列区域） |
| `?chrome=0` | 隐藏左下角「在线演示」横幅（截图用） |
| `?debug=1` | 横幅上实时显示演示层状态（`items=5 {"done":2,...} job=running@31.7%`） |

> 验证演示层是否真的跑通：开 `demo/?autostart=1&debug=1`，看横幅上
> `items` 是否 +1、`job` 是否从 `running` 走到 `done`。
> 截图用的 `?freeze` 是刻意绕开计时器的——无头浏览器的虚拟时间会加速计时器，
> 而全新 profile 首次加载又慢，靠真实跑一遍无法稳定命中"跑到一半"那一帧。

## 带宽预算（为什么素材被抠得这么细）

国内轻量服务器默认只有 **3M 带宽 ≈ 375 KB/s**，"点开就能看"和"点开转圈 28 秒"的差别就在这里。

| | 优化前 | 优化后 |
|---|---|---|
| 首屏关键资源 | ~10.5 MB（≈28 秒） | **811 KB（≈2.2 秒）** |
| 站点总体积 | 15.8 MB | **6.5 MB** |
| 最大单文件 | 2.7 MB | 1.1 MB |

怎么做到的：

- **截图 PNG → JPEG**：7 张界面图从 5.3 MB 降到 0.8 MB（省 85%）。Edge 无头模式只能输出 PNG，
  所以 `shots` 阶段截完立刻转 JPEG（宽 1400，足够 2x 屏）并删掉 PNG，同时自动把
  `index.html` / `README.md` 里的引用改成 `.jpg`。
- **首屏视频去掉音轨**：首屏是 `muted` 自动播放，原片那条 103 kb/s 音轨纯属浪费，直接 `-an`
  （省约 260 KB）。分辨率不再下调——面板宽 340px，2x 屏需要 680 物理像素，再降就糊。
- **应用图标压到 256px**：项目根目录那张是 1.1 MB 的 1024px 原图，展示站只需要 256px（53 KB）。
- **删掉没人引用的文件**：`demo/media/full-demo.mp4` 曾经白占 1.9 MB，落地页用的是 `assets/` 里那份。
- **构建期硬闸**：`media` 阶段会计算首屏三件套总体积，超过 2.5 MB 直接构建失败
  （曾经因为漏了 `scale` 把 4K 源片直接编码，产出过 12 MB 的首屏视频）。

> 改素材或换截图后，跑一次全流程 `build_showcase.py`，这些约束会自动重新施加。

## 脱敏与体积约束

- **构建期自检**：`build_showcase.py` 生成假数据后会扫一遍真人姓名、云端 Voice ID、密钥尾号、
  外部 URL 与本机绝对路径，**命中就直接构建失败**，不会「静默发布」。
- **导出期自检**：`export_public_repo.py` 会把本机仓库导出一份可公开副本到
  `D:\LocalDigitalHuman-public`，并复扫一遍；导出**不修改本机工程**。
- 真人声音样本（`data/voices/*.wav`）已在 `.gitignore` 中排除，且已 `git rm --cached` 移出索引（磁盘文件保留）。
- 背景音乐用 ffmpeg 合成的氛围垫乐替代真实曲目，规避版权。
- 选 EdgeOne Pages 时注意其**单文件 25MiB 上限**（本站最大 1.1 MB），以及大陆流量走海外节点。

## 部署

见 [DEPLOY.md](DEPLOY.md)。
