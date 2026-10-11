# 本地数字人工作台 — 项目说明书（AGENTS.md）

> 本文件供 AI 编程助手（Kimi Code 等）快速理解项目。修改代码前请先通读本文件。

> **工程位置（2026-08-17）**：`D:\LocalDigitalHuman`（从 C 盘 `Documents\Codex\...` 整体迁出；`启动本地数字人.vbs` 与 `tools/restart-server.ps1` 均按自身所在目录定位，无需改动即可运行）。

## 项目定位

纯本地运行的数字人短视频生成工作台：输入文案 → 克隆声音合成语音 → 口型同步驱动数字人形象 → 叠加字幕/标题/人名条/B-roll/背景音乐 → 导出 4K/2K 成片 + 自动封面。支持任务队列整夜排队生成。

## 技术架构

单页 Web 应用，**无构建步骤、无框架**：

- **后端** `server.py`（约 6900 行）：Python 标准库 `http.server`，端口 `17860`，承载全部 API、静态文件、任务队列、素材库索引。
- **前端** `app.js` + `index.html` + `styles.css`：原生 JS，四个面板（工作台 / 声音模型 / 数字人形象 / B-roll 素材）+「组件与下载」弹窗。
- **启动方式**：`启动本地数字人.vbs` → 拉起 `server.py`（优先用安装目录内 `runtime\python\pythonw.exe`，不存在再回退 voiceV2Module 的 pythonw.exe）→ 以 Edge app 模式打开 `http://127.0.0.1:17860`。

## 精简安装包与组件下载（2026-08-17）

工程支持打包成给他人电脑的一键安装包（`installer/`）：安装器只带代码 + 口型 v2 模块（hdModule 代码与 checkpoints，不含 venv）+ ffmpeg + 嵌入式 Python，约 2.1GB staging；模型依赖首次启动时在「组件与下载」向导里联网按需下载。

- **路径三级解析**（server.py 顶部）：环境变量 > `local-config.json`（gitignore）> 默认候选（安装目录布局 `runtime/`、`modules/` 优先，本机旧路径兜底）。覆盖 ffmpeg / modulesRoot / voxcpmRoot / whisperModelDir / toolPython / defaultOutput / gpuMinFreeMB / modelBatchSize。改路径一律走 `config_path()` / `first_existing_path()`，不要再写死。
- **口型 v2 = hdModule**（v1 是 humanModule，安装包不带）；`discover_modules_root` 只要求 hdModule 存在。
- **对齐/转写子进程的 Python 不再固定 VoxCPM venv**：`find_python_with_package()` 按「配置指定 > hdModule venv > VoxCPM venv」顺序探测谁装了 faster_whisper/funasr（`python_has_package` 结果缓存，安装完成后会清缓存）。
- **安装向导后端**：`GET /api/setup/steps`（组件清单+状态）、`POST /api/setup/install {steps}`（后台线程跑 setup_runner，进度在 `/api/job?kind=setup`）、`POST /api/setup/cancel`、`POST /api/setup/config`（热写 local-config.json，显存阈值免重启生效，`wait_for_gpu_memory` 动态读取）。
- **下载走 ModelScope 文件直链** `https://modelscope.cn/models/{repo}/resolve/master/{path}`（支持 Range 断点续传）：whisper CT2 模型 → `data/models/faster-whisper-large-v3-turbo`；bge（`AI-ModelScope/bge-small-zh-v1.5`）/ clip（`openai-mirror/clip-vit-base-patch32`）→ `data/models/` 下原目录。faster-whisper 用 pip 装进 hdModule venv（清华镜像）。
- **pythonEnv 步骤**：找不到 Python 3.10 时自动下载官方安装器静默装到 `runtime/python310` 再 `-m venv modules/hdModule/venv`（hdModule 的 pyd 是 cp310 编译，必须 3.10）。**venv 布局兼容**：原模块是 conda 布局（python.exe 在 venv 根目录），新建标准 venv 在 `Scripts/` 下，`venv_python_exe()` 两种都认。torch wheel 3.5GB 不走 pip 直连（断点续传不稳+文件锁），由 `download_with_resume`（带完整性校验和自动重试）下载后本地安装；requirements.txt 漏了 torchvision/torchaudio（需另外装 0.23.0/2.8.0 cu128）；insightface 无官方 Windows wheel，用 Gourieff/Assets 的社区预编译 wheel（源码编译需要 MSVC，目标机没有）。
- **前端降级**：无 humanModule 隐藏 V1 画质；无本地语音引擎隐藏「克隆本地声音」；核心组件（hdModule+venv+ffmpeg）未就绪时「添加并自动开始」拦截并弹安装向导，首启自动弹一次。
- **安装包构建**：`installer/build-staging.ps1` 组装 `installer/staging`（注意 ps1 必须 ASCII 或无 BOM 问题——Windows PowerShell 5.1 把无 BOM UTF-8 当 GBK 解析），`installer/setup.iss` 用 ISCC 编译（装到 `{localappdata}\Programs\LocalDigitalHuman`，免管理员；中文语言文件 ChineseSimplified.isl 需手动放进 Inno 的 Languages 目录）。**坑**：嵌入式 Python 的 `._pth` 不会把脚本目录加进 sys.path，server.py 必须保持只依赖标准库。
- **封面组件随包内置**（2026-08-17 E2E 实测暴露）：封面生成（`generate_video_cover`）需要 cv2 + PIL + numpy，而目标机的嵌入式 Python 只有标准库，会报"封面图片组件没有安装"。build-staging.ps1 在组装时给嵌入式 Python 打开 `._pth` 的 `Lib\site-packages` + `import site`，用 get-pip 引导后 pip 安装 `pillow opencv-python-headless==4.12.0.88`（numpy 随依赖带入，清华镜像），多占约 130MB。**必须钉 4.12 版本**：OpenCV 5.x 删除了 `cv2.CascadeClassifier`，封面代码依赖它（2026-08-17 对方机器实测踩坑）。server.py 其余部分仍只依赖标准库。
- **VC++ 运行库随包内置**（2026-08-18 对方机器实测暴露）：全新 Windows 缺 VC++ 2015-2022 运行库（torch/onnxruntime/opencv 都依赖），且旧版/损坏的 redist 会挡住新 redist 安装、aka.ms 官方源国内直连不稳——所以不走系统级安装。build-staging.ps1 从本机 System32 提取 10 个 DLL（vcruntime140*/msvcp140*/concrt140/vccorlib140，约 3MB）打进 `runtime/vcredist/` 并放入嵌入式 Python 目录；`setup_step_python_env` 建 venv 后把 DLL 复制到 venv 的 python.exe 旁边（应用级部署，exe 同目录 DLL 优先加载，完全不碰系统）。
- **依赖版本兼容**：目标机装的都是最新版依赖，本机是老版本，踩过两个坑——`broll_classifier.py` 的 `get_image_features/get_text_features` 在新版 transformers 返回 ModelOutput 对象而非张量（已用 `as_tensor()` 兼容两版）；OpenCV 见上。给目标机新增 pip 依赖时必须钉版本。
- **离线组件包**（2026-08-17）：大体积下载项可提前打成「组件离线包」随安装器分发，向导识别后本地安装/拷贝，全程不联网。目录约定：`组件离线包/python/python-3.10.11-amd64.exe`、`wheels/`（torch 2.8.0+cu128、torchvision 0.23.0、torchaudio 2.8.0、insightface 0.7.3 的 cp310 whl）、`models/<模型目录名>/`（目录名与 `MODEL_DOWNLOADS` 目标目录一致；注意 bge 的 `1_Pooling/config.json` 是嵌套路径，匹配必须用相对路径不能只看父目录名）。后端：`setup_bundle_dir()`/`bundle_file()`/`bundle_glob()`/`bundle_snapshot()`（环境变量 `LOCAL_DH_SETUP_BUNDLE` > local-config.json `setupBundleDir` > 自动探测 APP_DIR 内/旁「组件离线包」）；`setup_step_python_env` 四个下载点与 `setup_download_models` 都是"离线包有就用本地、没有走原下载"。前端：向导里「离线组件包」区块 + `/api/pick {kind:"folder"}` 选目录 + `/api/setup/config` 热写（`setupBundleDir` 已加白名单）。离线包本体在 `installer/output/组件离线包/`（不入 staging、不入 git），7z 分卷传百度云。

## 生成管线（main_task，server.py 内）

1. `validate_payload` 校验参数（本地声音解析出 `voiceEngine`）
2. `generate_segmented_script_audio`：文案自动分段（本地 180 字/段，ElevenLabs 1200 字/段），**支持断点续跑**（temp/voice-checkpoints）
3. **声音生成后必须 `stop_local_voice()` 释放显存**，再跑口型模型（RTX 3080 10GB，`GPU_MIN_FREE_MB=6500`）
4. `run_digital_human`：调用外部模块口型同步（`model_worker.py` 子进程）
5. ASS 字幕/标题/人名条 + 智能 B-roll（`plan_broll_segments`）+ 背景音乐混音
6. `export_resolution` 导出 4K/2K，`generate_video_cover` 自动选帧生成封面

## 双声音引擎（2026-08-13 新增 VoxCPM）

声音记录（`data/voices/voices.json`）带 `engine` 字段：`"v2"`（默认，旧引擎）或 `"voxcpm"`。

| | v2（原有） | voxcpm（新增） |
|---|---|---|
| 服务 | `D:\LocalDigitalHuman\modules\voiceV2Module\venv\python.exe api.py` | 项目内 `voxcpm_service.py` |
| Python | 该模块自带 venv（3.11 + torch 2.8.0+cu129） | `D:\LocalDigitalHuman\runtime\voxcpm\venv311\Scripts\python.exe`（同版本 torch，从 voiceV2Module 复制而来） |
| 端口 | 8001 | 8002 |
| 接口契约 | `GET /health` → `{model_loaded}`；`POST /generate` → `{code:200,data:{output_path}}` | 相同 |
| 克隆方式 | prompt_audio + prompt_text | VoxCPM2：有对照文本走 ultimate 模式，无文本走 reference-only |
| 语速 | 原生支持（0.5–2.0） | ffmpeg atempo 后处理（0.5–2.0） |

- 模型权重：`D:\LocalDigitalHuman\runtime\voxcpm\models\VoxCPM2`（来自 ModelScope `OpenBMB/VoxCPM2`，约 4.7GB；HuggingFace 在本机不可达）
- 引擎路由：`server.py` 的 `start_local_voice(kind, engine)` / `generate_local_voice(..., engine=...)`，同一时刻只运行一个声音服务，切换引擎自动停旧启新。
- `cleanup_stale_voice_processes` 同时清理两种引擎的遗留进程。
- 克隆模式（VoxCPM）：声音记录有 `promptText`（样本对照文本）→ 极致克隆（ultimate）；只有样本 → 参考克隆。"音色设计"（无样本文字描述音色）不适合声音档案，未开放。克隆弹窗可选模式并展示三者说明。
- 样本转写：`tools/transcribe.py`（FunASR SenseVoiceSmall，**CPU 运行不占显存**，模型约 900MB 在 `~/.cache/modelscope`）；端点 `POST /api/voice/transcribe {voiceId}`（ffmpeg 先转 16k 单声道 wav 再子进程转写，超时 900s 容忍首次下载）；`POST /api/voice/set-transcript {id, promptText}` 补录/修改对照文本（改名弹窗内置入口）。

## 字幕逐字对齐（2026-08-14；2026-08-15 新增 Whisper 引擎）

字幕/B-roll 不再按"字数+标点权重"估算时间（段内会越配越偏），改为逐字强制对齐：

- **双引擎**（`align_subtitle_cues` 按顺序尝试，全部失败才抛异常走旧估算）：
  1. `tools/align_whisper.py`（**默认优先**）：faster-whisper `large-v3-turbo`（ModelScope `pengzhendong/faster-whisper-large-v3-turbo`，CT2 格式 1.6GB 在 `~/.cache/modelscope`；CUDA float16，显存不足自动回退 CPU int8）。Whisper 只产词级时间戳，再与文案净字符流做 difflib 锚定：equal 块直接取识别时间，**replace 块（同音错字）直接用识别侧该词的时间区间，delete 块（漏字）在锚点间插值**，识别错字不污染对齐；匹配率 <50% 主动报错让上层回退。**实测 407 秒音频全程 29 秒**（含模型加载）。注意：漏字块的右锚点可能与左锚点零间隙，`t1 <= t0` 时必须保底正向步长，否则一个字符会被拉到音频末尾、后续全部压塌（2026-08-15 实测踩过）。
  2. `tools/align_subtitles.py`（回退）：FunASR `iic/speech_timestamp_prediction-v1-16k-offline`（**CPU 运行**，首次运行自动下载到 `~/.cache/modelscope`）；**该模型只在 ≤15 秒短音频上可靠**（99 秒音频实测尾部被压缩 12 秒），长音频走两遍分块对齐：能量静默点切 ≤12 秒的块 + 按块时长比例分配字符跑第一遍（已贴住真实时间轴），再把块边界挪到真实停顿处跑第二遍。
- 两引擎输入输出契约一致：输入 (分段音频, 该段文案)，输出与「去除标点空白后字符」一一对应的毫秒级时间戳；音频先经 ffmpeg 转 16k 单声道 wav（ffmpeg 路径由 server.py 在请求 JSON 里传入）。faster-whisper 只装在 VOXCPM venv311（连同 torch 2.8.0+cu129 / ctranslate2 4.8.1）。
- `server.py` 的 `align_subtitle_cues(segments, part_paths)`：声音分段生成后（`generate_segmented_script_audio` 内，只要字幕或 B-roll 开启）逐段对齐，按字符流顺序把时间戳切给 `subtitle_chunks` 的各分句；某段字符数对不上则该段回退段内权重分配，整体失败回退旧估算（记日志）。子进程调用统一走 `run_align_engine`（Whisper/FunASR 共用，含取消穿透与超时）。
- 对齐结果存 `data["subtitleCues"]`：ASS 字幕写入（`precise_cues` 优先于 `build_subtitle_cues`）与 `plan_broll_segments(..., cues=...)`（B-roll 窗口与检索 query 同步变准）共用。
- 用 VOXCPM 的 venv python 跑对齐子进程（funasr 只装在那个环境）。
- **管道死锁教训（2026-08-15 修复）**：对齐子进程输出必须重定向到日志文件（`temp/subtitle_align_*.log`）再轮询退出码；绝不能 `stdout=PIPE` 又不实时读——FunASR/ModelScope 的日志和下载进度条会写满 64KB 管道缓冲区把子进程堵死，表现为任务卡死在"第 N 段声音已完成"。

## 自己录音模式（voiceMode="upload"，2026-08-15）

用户自己朗读文案录音，直接用真人音频驱动数字人，跳过 TTS（情感/断句 100% 真人）：

- 工作台"声音"卡的人物下拉最后一项是"🎙 自己录音"（`__upload__`），选中后隐藏语速/试听/引擎参数；`setUploadVoiceMode()` / `setVoiceMode('upload')`。
- 上传行（`#customAudioRow`，2026-08-16 起）位于"任务编辑器"卡文案框下方、**常驻显示**（原始输入端）；上传成功即自动切到 upload 模式。upload 模式下**文案可留空**：`validate_payload`/`append_task_to_queue` 对 upload 放行空文案，空文案时服务端强制关掉字幕与 B-roll（没有文字可对准），队列标题回落为"录音 <文件名>"。
- 上传端点 `POST /api/audio/upload`（multipart，留在 `temp/uploads`，**不**像音乐那样移入素材库），返回 `{path, name, duration}`；试听走 `/api/media`，`allowed_media_path` 已放行 UPLOAD_DIR 内文件（2026-08-16 修复，此前上传后预览 404）。
- 服务端：`validate_payload` 校验 customAudio 必须在 UPLOAD_DIR 内；`prepare_uploaded_script_audio` 把录音转 44.1k wav 缓存进语音断点目录（`voice_checkpoint_dir` 按录音文件指纹区分），整段录音 + 整篇文案走 `align_subtitle_cues` 长音频两遍分块对齐，之后管线与 TTS 完全一致（merge → 口型 → ASS → 导出）。
- 队列 payload 持久化 `customAudio`（`stored_queue_payload`）；`freeze_queue_voice_selection` 显示"自己录音"；preview（试听）对 upload 模式直接报错（无意义）。
- 注意：录音文件在 temp/uploads，被手动清理后队列里未运行的 upload 任务会报"录音文件不存在，请重新上传"。

## 横版（16:9 / 4:3）字幕适配（2026-08-15）

`create_text_overlay_ass` 里 `width > height` 即横版：**不加标题**（title 强制清空）；字幕样式 Alignment 2 底部居中、MarginV ≈ 6.5% 高度（电影字幕位），字号为短边 × 0.046（比电影规格略大，手机可看清）。竖版逻辑不变。

## 口型模型输入分辨率（2026-08-15 上调）

`prepare_avatar_for_model` 的 `max_long_edge = 1920`（原 1280）：原视频先压到长边 1920 再喂模型，导出再 lanczos 放大到 2K/4K——所以 4K 成片是放大出来的，1920 上限是为减轻放大糊感在显存/内存安全内的折衷。profile 字符串含分辨率参数，改值会自动重建 `data/model-inputs` 缓存。

## 工作台声音参数面板（2026-08-13）

工作台"声音"卡片按所选声音的来源显示真实可调参数（`renderVoiceEngineParams` / `updateElevenParamsAvailability`）：

- **v2**：情感强度（emotionWeight 0–1）、情感描述（emotionText）；v2 服务原生支持。
- **voxcpm**：贴合度（cfgValue 1–5）、推理步数（inferenceTimesteps 4–30）；透传到 `voxcpm_service.py`。
- **ElevenLabs**：稳定性 / 相似度 / 风格强度 / 说话者增强（0–100 滑条）+ 语速。`eleven_v3` 不支持 style/speakerBoost（UI 停用）；`v3_voice_match` 双阶段模式下稳定性/相似度被服务端强制覆盖，UI 停用并提示，仅语速生效。
- 语速范围按来源动态切换：本地 0.5–2.0，ElevenLabs 0.7–1.2（API 上限）；`updateSpeedRange(provider)`。
- 持久化：本地引擎参数存 localStorage（`localDhVoiceParams:<voiceId>`）；ElevenLabs 的 settings 写回声音记录（防抖 800ms POST `/api/voice/save-elevenlabs`，与"声音参数"弹窗同一数据源），语速仍存 localStorage。
- 全链路透传：`validate_payload` → `generate_local_voice` / `generate_elevenlabs_voice`；队列 payload 持久化这些字段（`stored_queue_payload`）。

## 人物分组（2026-08-13）

素材按"人物"（讲师A / 讲师B / 讲师C / 讲师D……）分组管理：

- `data/persons.json`：人物记录 `{id, name, createdAt}`；端点 `GET /api/persons`、`POST /api/person/save`（改名/新建，同名拦截）、`POST /api/person/delete`（删除后其素材自动回落未分组）。
- 声音 / 形象 / B-roll 三类记录都带 `personId`（`""` = 未分组）；注意各 `load_*_records` 用白名单重建，新字段必须加进白名单。归类端点统一为 `POST /api/asset/set-person {kind: voice|avatar|broll, id, personId}`。
- 工作台"声音"卡与"数字人形象"卡都是**两级下拉**（先选人物、再选该人物名下的声音/形象）；`renderVoicePersonSelect` / `renderWorkbenchVoiceOptions` / 形象侧对称函数；`setVoice`/`setAvatar` 末尾同步下拉。
- 声音库 / 形象库面板按人物分组渲染（`.library-person-section`）；人物管理弹窗 `#personModal`；归类入口：改名弹窗（renameModal 人物下拉）、克隆/添加声音弹窗、B-roll 编辑弹窗。
- B-roll：`plan_broll_segments(..., person_id=...)`，主任务按所选形象的 `avatarPersonId`（validate_payload 从 avatarId 解析）优先匹配该人物素材，无候选则回落全部（旧行为不变）。
- ElevenLabs 额度显示：payg（按量付费）账号不按 `limit-used` 显示余量（会错显 0），显示"按量付费 · 本月已用 X 字符"；前端进入工作台自动后台同步超过 30 分钟未刷新的账号（`autoSyncStaleElevenAccounts`）。
- ElevenLabs 计费账本（2026-08-16 校准）：生成中本地即时累加（`record_elevenlabs_usage`）；TTS 按字符数，**STS 转换按 450 额度/分钟音频**（按平台真实用量反推约 430，原 1000/分钟高估一倍多）；每条队列任务结束后 `task_queue_worker` 自动 `sync_elevenlabs_account` 对齐平台真值（失败只记日志不影响队列）。

## 界面动效（ui-fx.js，2026-08-14）

`ui-fx.js`：react-bits 动效的原生移植，**无第三方依赖**（项目无构建步骤，不能直接用 React 组件）：Spotlight Card（鼠标坐标写入 `.fluent-card` 的 `--mx/--my`）、面板切换卡片错落入场、Specular Button 镜面高光描边、LightRays 全页 WebGL 光束背景（原生 WebGL，不用 OGL）。系统开"减弱动态效果"时全部自动禁用。整体配色为深色底 + 冷色光晕（参考 react-bits 官网截图调过一轮：矩形框描边、左侧栏透明化统一色调）。

## ElevenLabs 专业克隆（PVC）限制（2026-08-15）

- 声音记录新增 `category` 字段（来自 ElevenLabs 账号同步的 `normalize_elevenlabs_remote_voice`，注意 `load_voice_records` 白名单、`public_voice`、`save_elevenlabs_voice` 三处都要带上）。
- **未微调（fine-tuning 未做/被重置）的专业克隆声音只能被 V3 系使用**——multilingual_v2 / turbo_v2 直接报 `voice_not_fine_tuned`；在官网删除/重建模型后**连 V3 也会拒**（实测）。前端 `defaultElevenModeForVoice(voice)`：`category === 'professional'` 时默认生成模式强制 `v3_voice_match`（调用点：`setVoice` / `restoreDraft` 的 fallback）。
- 讲师D账号（creator 131000 字符/月）与声音已配置，参数同讲师A；其声音 `DEMO_VOICE_ID_NOT_REAL` 当前因官网模型被删处于不可用状态。


## 外部依赖（2026-08-18 起全部迁到 D 盘工程内）

- **轻语IP智能体（`C:\Program Files\aigc-human`）已于 2026-08-18 卸载删除**；口型/声音模块与 ffmpeg 迁入工程：`D:\LocalDigitalHuman\modules\`（hdModule + voiceV2Module）、`D:\LocalDigitalHuman\runtime\ffmpeg\`、`D:\LocalDigitalHuman\runtime\voxcpm\`。路径经 `local-config.json` 显式指定（modulesRoot / ffmpegDir / voxcpmRoot / whisperModelDir），server.py 的默认候选（`APP_DIR\modules`、`APP_DIR\runtime\ffmpeg\bin`）也能自动命中；C 盘旧路径只剩代码里的兜底候选，不再有实际文件。
- ModelScope 缓存迁到 `D:\LocalDigitalHuman\data\modelscope-cache`（用户环境变量 `MODELSCOPE_CACHE` 已指过去），whisper / SenseVoiceSmall / 时间戳预测模型都在其 `hub\models` 下；`C:\Users\w1227\.cache` 下的 modelscope 与 huggingface 缓存已删除。
- 启动链路：`启动本地数字人.vbs` 与 `tools/restart-server.ps1` 的兜底 pythonw 已改为 `modules\voiceV2Module\venv\pythonw.exe`；voxcpm venv311 的 `pyvenv.cfg` home 指向迁移后的 voiceV2Module venv（venv 迁移后必须检查这一项）。
- 备选模块根：`E:\讲师A数字人\本地附加文件3.1.0完整版\python-modules`（见 `MODULE_CANDIDATES`，仅兜底，无实际使用）
- 可选 Python 包：jieba（字幕断句）、psutil（进程清理）
- ElevenLabs：云端备选，API Key 用 Windows DPAPI 加密存储

## 数据与目录

- `data/`：avatars / voices / music / broll / models（bge-small-zh、clip-vit）/ fonts / face-cache，均为 JSON 索引 + 文件
- `data/task-queue.json`：任务队列持久化；ElevenLabs 密钥在内存 `QUEUE_SECRETS`，重启后云端任务需重新提交
- `temp/`：任务临时文件（可清理）；`logs/`：运行日志（`voice-voxcpm.log` 是 VoxCPM 服务日志）
- 默认输出目录：`D:\数字人视频输出`（`DEFAULT_OUTPUT`，2026-08-17 从工程内 `视频输出/` 迁出，C 盘瘦身；前端 `restoreDraft` 会把旧草稿里的 C 盘路径自动改写到新默认）；`backups/`：**每次大改前按 `before-<特性>-<日期>` 备份 server.py / app.js / index.html / styles.css**

## 队列任务控制（2026-08-14）

- 全局 `MAIN_CANCEL` Event + `TaskCancelled` 异常 + `raise_if_main_cancelled()` 检查点（分段合成循环、字幕对齐子进程轮询、口型子进程输出循环、导出 ffmpeg 轮询、`wait_for_gpu_memory` 及 main_task 阶段边界）；命中即终止子进程树（`kill_process_tree`）并向上抛出。
- **吞异常陷阱**：`data["subtitleCues"]`、`plan_broll_segments` 外层的 `except Exception` 之前都必须有 `except TaskCancelled: raise`。
- 运行中任务可"停止"（`cancel`）或"删除"（`delete`/`remove`）：`apply_queue_action` 置 `MAIN_CANCEL`；`main_task` 的 `except TaskCancelled` 分支停声音服务 + 清理进程释放显存，且 finally 里取消时**不再** `schedule_voice_warmup`（否则 3 秒后声音服务又被拉起占 4-5GB）。
- `task_queue_worker` 取新任务时 `MAIN_CANCEL.clear()`；`/api/start` 启动前也 clear。worker 收尾用 `MAIN_CANCEL.is_set()` 判定落库状态为 `cancelled`，且更新 item 前必须 `if item in QUEUE_ITEMS`（删除运行中任务会先移出列表）。
- 前端单条任务耗时：done/error/cancelled 显示"耗时"（finishedAt-startedAt，不含排队等待；从未启动就结束的回退 createdAt）、running 显示"已进行"（从 startedAt 起算）、pending 显示"已等待"（`queueItemTiming`，快照里自带 createdAt/startedAt/finishedAt）；running 行有"停止"按钮（带 confirm，语音断点续跑使重跑代价小）。
- **worker 崩溃防护（2026-08-16）**：worker 线程裸死会让队列假死（任务永远卡 running、停止按钮无效；pythonw 无 stderr 无从排查）。现为 `task_queue_worker` 外壳循环自动重启 + `threading.excepthook` / `log_unhandled_exception` 落盘 `logs/server-error.log`。`/api/queue` 快照会把 main job 的 stage/progress 叠加到 running 项上，job 是旧状态时 running 项会显示过期错误文案，勿误判。
- **队列有待跑任务时不预热声音模型（2026-08-16）**：`main_task` finally 里仅当队列无 pending 才 `schedule_voice_warmup(3)`——否则任务一失败就预热拉起 v2 声音服务占 4-5GB，下一条任务的 `wait_for_gpu_memory`（`GPU_MIN_FREE_MB=6500`）必挂，形成连环失败。桌面占用也会顶爆该阈值：2026-08-16 实测 dwm 泄漏 2.4GB + Chrome 1.9GB 时空闲仅约 6.3GB，任务直接报显存不足，需关 Chrome 或重启电脑。
- **声音服务闲置自动释放（2026-08-16）**：`schedule_voice_stop(stamp, delay=300)`——delay 秒内 `VOICE_LAST_USED` 没前进（没有任何生成用过服务）就 `stop_local_voice` + `cleanup_orphan_voice_processes()`；主任务持锁（RUN_LOCK）或克隆进行中时不释放、60 秒后重新检查。挂载点：预热（`warm_local_voice`，含启动预热和任务后预热）、克隆结束（`clone_voice_task` finally）、试听结束（`preview_task`）。主任务流程本身在声音合成完就显式 `stop_local_voice()` 再跑口型。口型模型是每任务子进程，finally 里 `cleanup_stale_model_processes` 清理，无常驻问题。
- **孤儿声音进程清理（2026-08-16）**：`cleanup_orphan_voice_processes()`——服务器被强杀/重启后，旧实例拉起的声音服务（v2 `api.py`、VoxCPM `voxcpm_service.py` 及其多进程子进程）会变孤儿常驻占显存内存。判定：沿父进程链向上穿过声音服务自己的子进程，链条断了（父进程已死）才是孤儿，按进程树 taskkill；链条尽头是任何活着的进程（当前 server.py、轻语等外部程序）都不动。挂载点：`main()` 启动时、闲置自停触发时。

## 修改约定（重要）

1. **版本管理**：项目已纳入 git（`main` 分支，2026-08-13 初始化）。大改前先确认当前改动已提交；完成一个特性后提交语义化中文 commit。`backups/` 里的历史手动备份仅作存档，不再新增。
2. 改前端后**必须 bump `index.html` 里的缓存版本号**（`app.js?v=`、`styles.css?v=`）。
3. Windows 环境：注意 GBK/UTF-8 编码、路径含空格要加引号、Git Bash 会把 `/c`、`/E` 误转成路径。
4. 显存是稀缺资源：声音服务与口型模型不能同时占显存，新增功能如涉及 GPU 必须遵守"先停声音服务再跑口型"的顺序。
5. 队列任务的 voice/engine 在 `validate_payload` 运行时解析，不存进队列 payload。
6. 修改后验证：`python -m py_compile server.py`；前端用浏览器控制台看报错。

## 常用调试入口

- 服务健康：`curl http://127.0.0.1:17860/api/ping`、`:8001/health`、`:8002/health`
- 队列状态：`GET /api/queue`；任务进度：`GET /api/job?kind=main|preview|clone`
