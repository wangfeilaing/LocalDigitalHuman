# 把展示站发布到公网（面试官点开即看）

> 目标：面试官在中国大陆**不需要任何代理/VPN**、点开一个链接就能看到项目介绍 + 可点界面演示 + 成片视频。
> 本文只讲「怎么发出去」。展示站本身的内容在 `showcase/`，构建方式见 `showcase/README.md`。

## 一、先说结论（为什么不能直接丢到 Vercel）

调研了当前各平台的真实可用性（2026-08 复核，附官方依据）：

| 方案 | 大陆直连 | 免备案 | 放 mp4 | 成本 | 结论 |
|---|---|---|---|---|---|
| **国内轻量云服务器 + `http://IP:8080`** | ✅ | ✅ | ✅ 无限制 | ¥38–99/年 | **首选** |
| EdgeOne Pages 免费版 + 自有未备案域名 | ✅（走海外节点） | ✅ | ⚠️ 单文件 ≤25MiB | 免费 + 域名 ¥10–30/年 | 备选 |
| 阿里云 OSS 默认域名 | ✅ | ✅ | ✅ | 按量 | ❌ `text/html` 被强制下载，入口页打不开 |
| 腾讯云 COS 默认域名 | ⚠️ | ✅ | ❌ | 按量 | ❌ 2024 年起**任意文件**强制下载 |
| GitHub Pages / Vercel / Netlify | ❌ 需代理 | ✅ | ✅ | 免费 | ❌ 正是要避免的 |
| Gitee / AtomGit Pages | — | — | — | — | ❌ 均已停服 |
| 七牛 / 又拍云测试域名 | ✅ | ✅ | ⚠️ | 免费 | ❌ 30 天回收、限速，不可生产 |

关键依据：
- EdgeOne Pages 官方文档：加速区含中国大陆时系统链接**仅 3 小时有效**；选「全球可用区（不含中国大陆）」时**默认 `*.edgeone.app` 域名在大陆返回 401**，必须绑自定义域名；配额为**单文件 25 MiB**（[域名概览](https://edgeone.ai/document/175201428435140608)、[配额说明](https://edgeone.cloud.tencent.com/pages/document/176994654809202688)）。
- 阿里云 OSS 默认域名对 `text/html` 强制下载，绑自定义域名需 ICP 备案（[官方 FAQ](https://help.aliyun.com/zh/oss/how-to-ensure-an-object-is-previewed-when-you-access-the-object)）。
- 腾讯云 COS 2024-01-01 后创建的桶，默认域名访问任意文件都带 `Content-Disposition: attachment`（[公告](https://cloud.tencent.com/document/product/436/96243)）。
- 备案检测针对**域名**（80 端口读 Host、443 看 SNI）；直接用公网 IP + 非标准端口不触发（[V2EX 实测](https://global.v2ex.co/t/1180965)）。

> 本展示站已按带宽预算控制体积：**总 6.5 MB，最大单文件 1.1 MB，首屏关键资源 811 KB**。
> 为什么抠这么细：国内轻量服务器默认只有 **3M 带宽（≈375 KB/s）**，首屏 811 KB ≈ **2.2 秒**；
> 如果不管，首屏会涨到 10 MB 以上（≈28 秒），面试官只会看到转圈。

---

## 二、方案 A：国内轻量服务器 + IP:8080（推荐）

### 步骤 1｜买一台最便宜的轻量服务器
- 阿里云「轻量应用服务器」或腾讯云「轻量应用服务器」，选 **2 核 2G / 3M 带宽 / Ubuntu 22.04**，38 元/年或 99 元/年档完全够用（纯静态站）。
- **带宽比 CPU 重要**：如果只有 3M 档，务必按下面的「带宽预算」保持素材精简；
  能选 5M 以上更从容（本站首屏 811 KB，5M 下约 1.3 秒）。
- **不要**买带域名的套餐（会牵扯备案），只买服务器 + 公网 IP。

### 步骤 2｜放行 8080 端口
在云控制台的**防火墙/安全组**里加一条入站规则：`TCP 8080`、来源 `0.0.0.0/0`。

### 步骤 3｜一键上传并配置（推荐，替代原本的手工 4 步）
在**你自己的电脑**上打开 PowerShell，执行：

```powershell
cd D:\LocalDigitalHuman\showcase
.\deploy.cmd 你的公网IP
```

`deploy.cmd` 会自动：

1. 读 `build/site.json`，**组装整站**（门户页 + 各项目子目录）到 `D:\LocalDigitalHuman\_site\`
   ——会顺带做体积预算自检（首屏超 2.5MB 直接失败，防止哪次素材换大了让面试官盯转圈）；
2. 上传到 `/var/www/site`，并把生成好的 `_site.nginx.conf` 装到 `/etc/nginx/conf.d/site.conf`；
3. 在服务器上装 nginx（走发行版官方源，缺才装）、`nginx -t` 校验、设开机自启、放行 ufw/firewalld；
4. 体检门户页、每个已启用项目、以及视频资源，最后打印要发给面试官的链接。

> 之所以用 `.cmd` 包装：Windows 默认禁止运行 `.ps1`（"禁止运行脚本"），
> 包装脚本用 `-ExecutionPolicy Bypass` 起来，双击或命令行都能跑。
> 想直接跑 ps1 也可以：
> `powershell -NoProfile -ExecutionPolicy Bypass -File .\build\deploy_to_server.ps1 -ServerIp <IP>`
>
> 需要输入服务器密码（脚本不保存任何凭据）。想免密就先配 SSH 公钥：
> `ssh-keygen -t ed25519` 然后 `type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh root@<IP> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`

重复执行是安全的（会先删远端旧目录再传，不会多套一层）。只想体检线上：
`.\deploy.cmd 你的公网IP 8080 check`

### 服务器上的目录长这样

```
/var/www/site/
├─ index.html          门户页（面试官第一眼看到这个，列出所有项目）
├─ digital-human/      本地数字人工作台
└─ <slug>/             以后新增的项目，各自一个目录
```

所以最终链接是：门户 `http://IP:8080/`，本项目 `http://IP:8080/digital-human/`。

<details>
<summary>手工步骤（不想用脚本时）</summary>

#### 上传
```powershell
# 上传到 /var/www/ 下（scp -r 会把 showcase 整个目录放进去）
scp -r D:\LocalDigitalHuman\showcase root@<你的公网IP>:/var/www/
```
> 图形化替代：WinSCP / 宝塔面板，把 `showcase` 目录拖到 `/var/www/` 下。
> 上传后服务器上的入口必须是 `/var/www/site/index.html`。
> 重复上传时先 `rm -rf /var/www/site`，否则 `scp -r` 会再套一层。

#### 起静态服务（nginx，原生支持 Range，视频拖进度条正常）
```bash
sudo apt update && sudo apt install -y nginx
sudo tee /etc/nginx/conf.d/site.conf >/dev/null <<'EOF'
server {
    listen 8080 default_server;
    server_name _;
    root /var/www/site;
    index index.html;
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    location / { try_files $uri $uri/ =404; }
}
EOF
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
sudo systemctl enable nginx     # 开机自启，重启服务器后链接不会失效
```
> 如果你的后端项目也要挂上，在上面那个 server 块里加一段
> `location /项目名/ { proxy_pass http://127.0.0.1:端口/; }` 即可（脚本会自动生成）。
>
> **为什么用 nginx 而不是 Caddy**（实测换过一次）：Caddy 不在 Ubuntu 官方源里，
> 它的官方 apt 源（Cloudsmith）从这台服务器访问返回 402，并留下坏源导致后续
> `apt-get update` 全部失败；改用官方静态二进制，curl 又会卡在等连接关闭上。
> nginx 在每个发行版自己的源里都有，走云厂商内网镜像，秒级且有签名。
> 如果系统开了 ufw：`sudo ufw allow 8080`。
</details>

### 步骤 4｜验证
```powershell
cd D:\LocalDigitalHuman\showcase
.\deploy.cmd 你的公网IP 8080 check      # 脚本会自动体检门户/各项目/视频
```
- 电脑浏览器打开 `http://<你的公网IP>:8080/` → 门户页（作品列表）。
- 点进项目 → `http://<你的公网IP>:8080/digital-human/` 能看介绍页、能点演示、能跑模拟流水线。
- **必须用手机 4G/5G（关掉 WiFi）再打开一次**：这才是面试官的网络环境，能排除「本机 DNS/代理造成的假成功」。

### 这个链接长什么样
门户 `http://123.45.67.89:8080/`，各项目 `http://123.45.67.89:8080/<slug>/`。
不够好看，但**免备案、永久有效、零维护**。若想要短域名：买个便宜域名解析到该 IP 后仍走 `:8080` 端口——但**域名指向国内 IP 却不备案属于规避备案**，存在被限制的风险，面试场景建议直接用 IP 求稳。

---

## 二之二、一个服务器放多个项目

一个 2核2G 轻量服务器放**几十个静态项目**都没问题：静态文件几乎不吃 CPU 和内存，
真正的约束只有带宽与流量包。本项目从一开始就全用相对路径，所以挪到子目录下**零改动**
（实测：挂到 `/digital-human/` 下，首页/演示页/视频/图片/假数据全部 200 且渲染无损）。

### 怎么加一个项目

只改 `showcase/build/site.json`，然后重新部署：

```jsonc
{
  "projects": [
    { "slug": "digital-human", "title": "本地数字人工作台",
      "dir": "D:\\LocalDigitalHuman\\showcase", "kind": "static", "enabled": true,
      "tagline": "...", "description": "...", "tags": ["..."] },

    // 新增静态项目：把构建产物目录指过去即可（相对路径会自动适配）
    { "slug": "my-dashboard", "title": "数据看板",
      "dir": "D:\\MyDashboard\\dist", "kind": "static", "enabled": true,
      "tagline": "...", "description": "...", "tags": ["..."] },

    // 需要后端的项目：kind 改成 proxy 并给出后端端口
    { "slug": "student-delivery", "title": "学员交付管理系统", "dir": "",
      "kind": "proxy", "backendPort": 3000, "enabled": true,
      "tagline": "...", "description": "...", "tags": ["..."] }
  ]
}
```

```powershell
.\deploy.cmd 你的公网IP        # 重新组装 + 上传 + 重载 nginx，不用手工碰服务器
```

门户页卡片、目录结构、nginx 配置全部由这份配置生成。两个开关配合使用：

- `enabled: true / false`：是否把该项目的文件传上服务器（`false` 显示为"即将上线"占位）；
- `visible: true / false`：是否在门户页露出（默认跟随 `enabled`）。
  **还没准备好、文案里还带 TODO 的项目一定要设 `visible: false`** —— 门户页是面试官看的第一屏，
  出现"待补充"这类字样是硬伤（这一条是把门户页做出来、发现自己的 TODO 被渲染上去之后才补的）。

### 三种组织方式怎么选

| 方式 | 链接长相 | 代价 |
|---|---|---|
| **路径（本方案默认）** | `http://IP:8080/digital-human/` | 一个 nginx 配置搞定，不用域名、不用备案、不用改项目代码 |
| 端口 | `http://IP:8081/` | 每个项目一个端口，链接难看，还要逐个放行安全组 |
| 子域名 | `dh.你的域名.com` | 要买域名 + 解析；国内 IP 上用 80/443 需备案，用非标端口属于规避备案，有风险 |

### 需要后端的项目要注意

`"kind": "proxy"` 的项目跑在**独立端口**上（不是挂在主站路径下）：

```jsonc
{ "slug": "student-delivery", "kind": "proxy",
  "backendPort": 3000,          // 后端进程实际监听的端口（只监听 127.0.0.1）
  "proxyPort": 3001,            // nginx 对外暴露的端口
  "maxBodySize": "500m" }       // 允许的上传体积
```

生成的 nginx 配置会多出一个独立的 server 块：

```nginx
server {
    listen 3001 default_server;
    client_max_body_size 500m;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}
```

**为什么不挂在 `/student-delivery/` 子路径下**（实测教训）：Next.js 这类应用的静态资源是
`/_next/...`、接口是 `/api/...`，全是**绝对根路径**。挂到子路径下要么整页 404，
要么必须改代码加 `basePath`——而这个项目里有 108 处 `fetch('/api/...')`，
加了 `basePath` 反而会和 `/api` 前缀打架。独立端口零代码改动、零风险。
代价是**要在云防火墙里多放行一个端口**（这里是 3001）。

在服务器上你还需要：

1. 把后端程序放上去（建议 `/opt/<项目名>/`）并装依赖；
2. 写一个 **systemd 服务**让它常驻并开机自启（裸 `nohup` 重启即失效），
   `EnvironmentFile` 指向 `.env`，`ExecStart` 直接调 `node_modules/next/dist/bin/next start -H 127.0.0.1 -p 3000`
   （不要用 `npm run start`，package.json 里的脚本自带 `-H 0.0.0.0`，会覆盖回环地址）；
3. 让后端**监听 `127.0.0.1` 而不是 `0.0.0.0`**（外面有 nginx 挡着，别把端口直接暴露）。

三个现实约束：

- **内存**：2核2G 跑一个 Node/Next 常驻进程实测只占 ~65MB，很宽裕；
  但再叠加 MySQL（约 400MB）就要盯内存。SQLite 方案没有这个问题。
- **构建内存**：Next.js 构建在 2G 机器上有 OOM 风险，先加 2GB swap 再构建（本项目已加）。
- **绝不要把生产库直接挂公网**：学员/客户数据属于个人信息。合规做法是准备一份
  **脱敏演示库**（保留表结构与关联关系，把姓名/手机号/身份证/银行账号/密钥等全部替换为
  程序生成的假值），并且**在生成后做交叉校验**：非保留列与原库零交集 + 格式扫描 + 姓名语境扫描。
  本仓库的 `showcase/build/` 里没有这个脚本（它是一次性工具），思路可直接照搬。

---

## 三、方案 B：EdgeOne Pages 免费版 + 未备案域名

适合不想买服务器、且能接受「大陆流量走海外节点（延迟略高）」的情况。

1. 注册腾讯云 EdgeOne，进入 **Pages / Makers** 控制台，新建项目 → 直接上传（或从 GitHub 仓库构建）`D:\LocalDigitalHuman\_site` 目录内容。
2. 加速区域选择 **「全球可用区（不含中国大陆）」**——这是唯一不需要备案的组合。
   ⚠️ 不要选含中国大陆的区域：那样系统生成的访问链接**只有 3 小时有效期**。
3. 平台会给你一个 `*.edgeone.app` 域名。**这个默认域名在大陆会返回 401**，必须继续第 4 步。
4. 买一个便宜域名（`.top` / `.xyz`，首年 10–30 元），在 EdgeOne「添加自定义域名」里绑定，按提示加 CNAME 解析、申请免费证书。
5. 等证书签发后访问 `https://你的域名/`，同样用手机 4G 复测。

注意：
- **单文件上限 25 MiB**（本站最大文件 1.1 MB，无压力）；账户总存储 5 GiB。
- 大陆访客走海外节点，首次打开可能 1–3 秒；面试前务必实测一次。
- 域名到期不续会直接失效，别忘了。

---

## 四、方案 C（加分项）：面试当天开「真机在线 Demo」

展示站永远是假数据。如果面试官想看**真的点一下文案就出片**，用内网穿透把本机的真程序映射出去：

1. 本机启动程序：双击 `启动本地数字人.vbs`（服务监听 `127.0.0.1:17860`）。
2. 装一个国内内网穿透客户端（cpolar / 花生壳 / frp 自建），把 **本机 17860** 映射为公网地址。
3. 客户端服务端通常支持加一层 **HTTP Basic Auth**——**必须开**，因为这个程序**完全没有登录鉴权**，暴露出去等于把显卡和素材库交给陌生人。
4. 面试时把临时链接发过去；面试结束立刻在客户端关闭隧道。

现实约束（说清楚以免翻车）：一次只能服务一个人；4K 导出要占用 RTX 3080 十几分钟；声音服务与口型模型不能同时占显存，**面试官和你不能同时生成**。

---

## 五、面试前 5 分钟自检清单

- [ ] **手机 4G** 打开主链接 → 首屏 ≤3 秒出画面（介绍页是响应式的，手机排版正常）
- [ ] 手机点「打开在线演示」→ 会看到**桌面界面整体缩放**的视图 + 一行「建议用电脑打开」提示，这是刻意设计：
      工作台是桌面端工具界面，演示页固定按 1280px 桌面宽渲染，手机上不重排、不横向溢出
- [ ] 电脑上打开演示页：切四个面板、切人物、点「开始生成」能看到进度条跑完并弹出成片
- [ ] **需要后端的项目（独立端口）也在线**：`http://IP:3001/` 能打开登录页，用门户卡片上写的
      演示账号能登进去（这个端口要在云防火墙里单独放行）
- [ ] 成片视频能播放、能拖进度条（nginx/EdgeOne 都支持 Range）
- [ ] 界面截图能点开看大图
- [ ] 把所有链接（门户、各项目、GitHub 仓库）整理成一段话放进简历/邮件
- [ ] 服务器已设开机自启（`systemctl enable nginx` + `systemctl enable <后端服务名>`），
      避免面试当天服务器重启后链接 502

## 五之二、面试官大概率会怎么点（提前自己走一遍）

1. 打开主链接 → 看 10 秒首屏，判断"这是干什么的"（所以首屏文案必须一句话说清）
2. 点「打开在线演示」→ 他会自己切到「声音模型」「数字人形象」「B-roll 素材」翻一翻
3. 回工作台点「添加并自动开始」→ 看进度条跑完、看成片（这一步最像"真的能用"）
4. 滚到「工程难点与解法」→ 这里是他判断你工程能力强弱的地方
5. 点「查看源码仓库」→ 看 README 与代码组织

> 第 5 步要求你先填好仓库地址（`showcase/index.html` 里 `#repoLink` 的 `data-repo`，
> 改这一处即可；没填时按钮显示「源码仓库 · 待公开」且不可点，不会让面试官点到 404）。

## 六、内容更新流程

改了界面或想换素材后：

```powershell
# 1. 重新生成演示站（转码素材 -> 脱敏假数据 -> 同步前端 -> 重新截图并转 JPEG）
& 'C:\Users\w1227\AppData\Local\Programs\Python\Python310\python.exe' `
  D:\LocalDigitalHuman\showcase\build\build_showcase.py

# 2. 本地先看一眼（或双击 showcase\预览展示站.cmd）
python -m http.server 8080 --directory D:\LocalDigitalHuman\showcase   # http://127.0.0.1:8080/

# 3. 重新上传（同一条命令，幂等）
.\deploy.cmd 你的公网IP
```

> 前端一改动，必须重跑 `frontend` 阶段——`showcase/demo/` 里的 `app.js` / `styles.css` 是**从项目根目录复制过来并打了补丁的副本**，不是软链接。
> 截图改动后必须跟着跑 `shots`（它负责 PNG→JPEG 转换与引用改写）；只跑 `shots` 不跑全流程也可以。

## 七、排错

| 现象 | 原因 | 处理 |
|---|---|---|
| 打开超时 | 安全组/防火墙没放行 8080 | 云控制台加规则 + `sudo ufw allow 8080` |
| 提示"禁止运行脚本" | Windows 执行策略 | 用 `deploy.cmd`（内部已 `-ExecutionPolicy Bypass`），或加 `-ExecutionPolicy Bypass` |
| 页面 404 目录列表 | 上传后多套了一层目录 | 脚本会自动先删远端旧目录；手工上传时先 `rm -rf /var/www/site` |
| 界面能开但图/视频裂 | 上传不完整或路径大小写 | 重新 `.\deploy.cmd <IP>` 覆盖上传 |
| 图片裂、路径带 .png | 只跑了 `shots` 但没转换/改引用 | 重跑 `build_showcase.py shots`（会一起改引用） |
| 视频不能拖进度 | 服务端不支持 Range | 用 nginx，别用简易 http.server 长期跑 |
| 打开是下载而不是网页 | 用了 OSS/COS 默认域名 | 换成本文的方案 A 或 B |
| 首屏加载很慢 | 带宽档太低或素材被换大 | 跑 `media` 阶段会做体积硬闸自检；或升到 5M 带宽 |
| `git push` 报 schannel / TLS 握手失败 | Git for Windows 默认用 schannel，会去查证书吊销列表，而国内连不上 CRL 服务器（报 `CRYPT_E_REVOCATION_OFFLINE`）；若同时挂着本地代理而其上游节点已挂，会更像"网络不通" | 在该仓库里执行 `git config --local http.sslBackend openssl` 与 `git config --local http.proxy ""`，然后多试几次（国内直连 GitHub 时通时断，实测第 5 次成功） |
| 演示页点按钮报「演示模式」 | 正常行为 | 静态站跑不了真实模型，真机能力见方案 C |
