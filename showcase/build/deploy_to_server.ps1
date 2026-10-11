# Publish the whole site (portal page + every project) to a mainland-China lightweight server.
#
#   Run it with:  ..\deploy.cmd <server-ip> [port] [check]
#   or directly:  powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy_to_server.ps1 -ServerIp 1.2.3.4
#
# Login user: defaults to "root". Tencent Cloud Linux images use "root" for CentOS-family
# and "ubuntu" for Ubuntu-family, so if root is refused try:
#   ... -ServerIp <ip> -User ubuntu
# The script auto-detects whether the login user is root and whether passwordless sudo
# works, then adapts the upload path and prefixes privileged commands accordingly.
# Key-pair instances: pass -KeyFile <path to .pem>.
#
# What it does (idempotent, safe to re-run):
#   1. preflight  - build the site tree from site.json, report size / first-paint budget
#   2. upload     - scp the generated _site tree and the generated nginx config
#   3. configure  - install nginx if missing, validate config, enable + restart
#   4. verify     - HTTP check the portal and every enabled project path
#
# Layout on the server:  /var/www/site/index.html          (portal)
#                        /var/www/site/<slug>/...          (one folder per project)
# Adding a project = edit site.json, re-run this script.
#
# Why a non-standard port: ICP filing checks target domain names (port 80 reads the
# Host header, 443 inspects SNI). Serving over http://<public-ip>:8080 avoids the
# filing requirement and needs no proxy/VPN on the interviewer's side.
#
# NOTE: keep this file ASCII-only. Windows PowerShell 5.1 decodes a BOM-less file as
# GBK, and non-ASCII bytes then corrupt strings and here-strings (see AGENTS.md).

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ServerIp,
    [int]$Port = 0,                      # 0 = take the port from site.json
    [string]$User = 'root',
    [string]$KeyFile = '',               # private key path, when the instance uses a key pair
    [switch]$VerifyOnly,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$BuildDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $BuildDir)   # showcase/build -> repo root
$SiteConfig = Join-Path $BuildDir 'site.json'
$Stage = Join-Path $ProjectRoot '_site'
$SiteConf = Join-Path $ProjectRoot '_site.nginx.conf'
$Remote = "$User@$ServerIp"
$SshOptions = @('-o', 'StrictHostKeyChecking=accept-new', '-o', 'ConnectTimeout=15')
if ($KeyFile) {
    if (-not (Test-Path $KeyFile)) { Write-Host "[X] key file not found: $KeyFile" -ForegroundColor Red; exit 1 }
    # BatchMode + PreferredAuthentications: a key must be enough, so never fall back to an
    # interactive password prompt. Without this, ssh silently blocks forever waiting for
    # input whenever it runs without a TTY (e.g. from an automation harness), which looks
    # exactly like a hang. It also turns "key not accepted" into a fast, clear error.
    $SshOptions += @(
        '-i', $KeyFile,
        '-o', 'IdentitiesOnly=yes',
        '-o', 'BatchMode=yes',
        '-o', 'NumberOfPasswordPrompts=0',
        '-o', 'PreferredAuthentications=publickey'
    )
}

function Step($text) { Write-Host "`n=== $text ===" -ForegroundColor Cyan }
function Ok($text) { Write-Host "  [OK] $text" -ForegroundColor Green }
function Warn($text) { Write-Host "  [!] $text" -ForegroundColor Yellow }
function Die($text) { Write-Host "  [X] $text" -ForegroundColor Red; exit 1 }

function Invoke-Ssh([string]$Command) {
    & ssh @SshOptions $Remote $Command
    if ($LASTEXITCODE -ne 0) { Die "remote command failed: $Command" }
}

function Get-SshOutput([string]$Command) {
    $output = & ssh @SshOptions $Remote $Command 2>&1
    return ($output | Out-String).Trim()
}

function Test-Site([string]$Url) {
    for ($i = 1; $i -le 12; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10 -MaximumRedirection 0
            if ($response.StatusCode -eq 200) { return $true }
        } catch {
            Start-Sleep -Seconds 5
        }
    }
    return $false
}

if (-not (Test-Path $SiteConfig)) { Die "missing site config: $SiteConfig" }
$config = Get-Content $SiteConfig -Raw -Encoding UTF8 | ConvertFrom-Json
if ($Port -eq 0) { $Port = if ($config.port) { [int]$config.port } else { 8080 } }
$enabled = @($config.projects | Where-Object { $_.enabled })
$base = "http://${ServerIp}:$Port"

function Assert-Paths {
    if (Test-Site "$base/") { Ok "portal page 200 -> $base/" } else { Die "cannot open $base/ : check the cloud firewall/security group for TCP $Port" }
    foreach ($project in $enabled) {
        if ($project.kind -eq 'proxy' -and $project.proxyPort) {
            # 需要后端的项目跑在独立端口上（Next.js 这类应用的资源路径是绝对根路径，
            # 挂在子路径下必然 404）。这个端口需要在云防火墙里额外放行。
            $proxyUrl = "http://${ServerIp}:$($project.proxyPort)/"
            if (Test-Site $proxyUrl) {
                Ok "/$($project.slug)/ -> $proxyUrl 200 (backend proxied)"
            } else {
                Warn "$proxyUrl not reachable - open TCP $($project.proxyPort) in the cloud firewall, and check the backend service"
            }
            continue
        }
        $url = "$base/$($project.slug)/"
        if (Test-Site $url) { Ok "/$($project.slug)/ 200" } else { Warn "$url not reachable" }
    }
    $video = "$base/digital-human/assets/hero.mp4"
    if (Test-Site $video) { Ok "video asset 200 (Range/file_server works)" } else { Warn "$video not reachable" }
}

# ---------------------------------------------------------------- verify only
if ($VerifyOnly) {
    Step "online check: $base/"
    Assert-Paths
    Write-Host "`nNext: turn OFF wifi on your phone, use 4G/5G, and open the same URL again." -ForegroundColor Yellow
    Write-Host "That is the only way to rule out a false success caused by local DNS or a proxy." -ForegroundColor Yellow
    exit 0
}

# ---------------------------------------------------------------- 1. build + preflight
Step "1/4 build site tree from site.json"
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) { Die 'ssh.exe not found - install the OpenSSH Client optional feature' }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Die 'python not found on PATH' }
if (-not $SkipBuild) {
    & python (Join-Path $BuildDir 'build_site.py')
    if ($LASTEXITCODE -ne 0) { Die 'build_site.py failed' }
}
if (-not (Test-Path (Join-Path $Stage 'index.html'))) { Die "missing $Stage\index.html - run build_site.py first" }
if (-not (Test-Path $SiteConf)) { Die "missing $SiteConf" }

$files = Get-ChildItem $Stage -Recurse -File
$totalMb = ($files | Measure-Object Length -Sum).Sum / 1MB
$largest = ($files | Sort-Object Length -Descending | Select-Object -First 1)
Ok ("{0} files / {1:N1} MB total, largest is {2} ({3:N0} KB)" -f $files.Count, $totalMb, $largest.Name, ($largest.Length / 1KB))
Ok ("{0} project(s) enabled: {1}" -f $enabled.Count, (($enabled | ForEach-Object { $_.slug }) -join ', '))

# First-paint budget: a 3M-bandwidth instance moves roughly 375 KB/s.
$budget = 0
foreach ($rel in @('digital-human\index.html', 'digital-human\assets\hero.mp4', 'digital-human\assets\app-icon.png')) {
    $candidate = Join-Path $Stage $rel
    if (Test-Path $candidate) { $budget += (Get-Item $candidate).Length }
}
Ok ("landing first-paint {0:N0} KB => about {1:N1}s on a 3M instance" -f ($budget / 1KB), ($budget / 1KB / 375))
if ($totalMb -gt 500) { Warn "site tree is larger than 500MB - check for stray raw assets before uploading" }

# ---------------------------------------------------------------- 2. login + capability probe
Step "2/5 probe login ($Remote)"
$uid = Get-SshOutput 'id -u'
if ($uid -notmatch '^\d+$') {
    Die @"
cannot run commands as $Remote (got: $uid)
  - If this is an Ubuntu image, the default user is usually 'ubuntu', not root. Retry with:
      -User ubuntu
  - If the instance was created with a key pair, add:  -KeyFile <path-to.pem>
  - Also check that port 22 is open in the cloud firewall.
"@
}
$remoteRoot = $config.remoteRoot.TrimEnd('/')
# NEVER call PowerShell's Split-Path on a Linux path: it returns Windows-style backslashes
# ("/var/www/site" -> "\var\www"), which silently creates a junk directory on the server and
# makes the following mv fail with "No such file or directory". Split on '/' by hand.
if ($remoteRoot -notmatch '/') { Die "remoteRoot must be an absolute Linux path, got: $remoteRoot" }
$remoteParent = $remoteRoot.Substring(0, $remoteRoot.LastIndexOf('/'))
if (-not $remoteParent) { $remoteParent = '/' }
if ($uid -eq '0') {
    $sudo = ''
    Ok "logged in as root"
} else {
    $probe = Get-SshOutput 'sudo -n true 2>&1 && echo SUDO_OK || echo SUDO_NEEDS_PASSWORD'
    if ($probe -notmatch 'SUDO_OK') {
        Die @"
logged in as uid $uid but passwordless sudo is unavailable.
Options:
  a) reset the 'root' password in the console and re-run with -User root and -KeyFile if needed;
  b) bind an SSH key to the instance and log in as root;
  c) as a temporary workaround, run this once in the console web terminal:
       echo "$User ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/90-$User
"@
    }
    $sudo = 'sudo '
    Ok "logged in as uid $uid with passwordless sudo"
}

# ---------------------------------------------------------------- 3. upload
Step "3/5 upload to $remoteRoot"
# The nginx config is always uploaded to the login user's home directory and installed by
# the setup script: /etc/nginx may not exist yet (nginx not installed), and scp cannot sudo.
Invoke-Ssh "rm -rf ~/site-upload ~/site.nginx.conf"
& scp @SshOptions -r $Stage "${Remote}:~/site-upload"
if ($LASTEXITCODE -ne 0) { Die 'scp upload of the site tree failed' }
& scp @SshOptions $SiteConf "${Remote}:~/site.nginx.conf"
if ($LASTEXITCODE -ne 0) { Die 'scp upload of the nginx config failed' }
# Drop the junk "\var\www" directory left behind by the earlier Split-Path bug.
Invoke-Ssh "${sudo}rm -rf '/home/$User/\var' '~/\var'"
Invoke-Ssh "${sudo}rm -rf $remoteRoot && ${sudo}mkdir -p $remoteParent && ${sudo}mv ~/site-upload $remoteRoot"
Ok "uploaded site tree + nginx config"

# ---------------------------------------------------------------- 4. configure nginx
Step "4/5 configure server (nginx static server + boot persistence)"
# Single-quoted here-string + placeholder replacement: bash $(...) must NOT be evaluated
# by PowerShell. Keep it that way. __SUDO__ becomes "" for root or "sudo " otherwise.
#
# Web server choice, after actually trying the alternatives on this instance:
#   * Caddy is not in the Ubuntu archive; its Cloudsmith apt repo answers 402 Payment
#     Required here and leaves a broken source that breaks every later apt-get update;
#   * the official static Caddy binary downloads but curl then hangs waiting for the
#     connection to close (no timeout) - not something to put in a deploy path;
#   * nginx ships in every supported distro's own repo, served by the cloud's internal
#     mirror (seconds, signed), and does everything this site needs.
$remoteTemplate = @'
set -e
PORT=__PORT__
ROOT=__ROOT__
S="__SUDO__"

install_nginx() {
  if command -v nginx >/dev/null 2>&1; then echo "nginx already present"; return 0; fi
  if command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    ${S}apt-get update -qq
    ${S}apt-get install -y -qq nginx
  elif command -v dnf >/dev/null 2>&1; then
    ${S}dnf install -y nginx
  elif command -v yum >/dev/null 2>&1; then
    ${S}yum install -y nginx
  fi
  command -v nginx >/dev/null 2>&1 || { echo "FATAL: nginx could not be installed" >&2; exit 1; }
  echo "nginx installed"
}

install_nginx
# A leftover caddy from an earlier attempt must never fight nginx for the port.
if command -v caddy >/dev/null 2>&1; then ${S}systemctl disable --now caddy >/dev/null 2>&1 || true; fi

# conf.d/ is included by nginx on Debian/Ubuntu and on RHEL alike.
${S}mkdir -p /etc/nginx/conf.d
${S}install -m 644 ~/site.nginx.conf /etc/nginx/conf.d/site.conf
# The distro default site listens on :80; harmless, but remove it so nothing surprises us.
${S}rm -f /etc/nginx/sites-enabled/default

${S}nginx -t
${S}systemctl enable nginx >/dev/null 2>&1 || true
${S}systemctl restart nginx
if command -v ufw >/dev/null 2>&1 && ${S}ufw status 2>/dev/null | grep -q "Status: active"; then ${S}ufw allow $PORT/tcp >/dev/null; fi
if command -v firewall-cmd >/dev/null 2>&1 && ${S}firewall-cmd --state >/dev/null 2>&1; then
  ${S}firewall-cmd --permanent --add-port=$PORT/tcp >/dev/null || true
  ${S}firewall-cmd --reload >/dev/null || true
fi
sleep 2
echo "nginx service: $(${S}systemctl is-active nginx)"
echo "nginx version: $(nginx -v 2>&1)"
echo "listening sockets on $PORT: $(ss -lnt 2>/dev/null | grep -c ":$PORT" || echo 0)"
ls -la __ROOT__/index.html
'@
# CAUTION: PowerShell variable names are CASE-INSENSITIVE. $Remote (the ssh target
# "user@host") and a lowercase $remote holding this script body are THE SAME VARIABLE -
# assigning the script text silently overwrote the ssh target, and ssh then received the
# script's first line ("set -e") as a hostname. Hence the distinct name below.
$setupBody = $remoteTemplate.Replace('__PORT__', "$Port").Replace('__ROOT__', $remoteRoot).Replace('__SUDO__', $sudo)
# The script is also shipped as a file rather than passed as one giant argv: a multi-line
# argument is fragile across PowerShell's native-command argument handling, and keeping the
# file on the server makes re-runs and debugging easy.
$setupPath = Join-Path $ProjectRoot '_site.setup.sh'
$setupScript = ($setupBody -replace "`r`n", "`n")
[System.IO.File]::WriteAllText($setupPath, $setupScript, [System.Text.UTF8Encoding]::new($false))
& scp @SshOptions $setupPath "${Remote}:~/site-setup.sh"
if ($LASTEXITCODE -ne 0) { Die 'scp upload of the setup script failed' }
Invoke-Ssh "bash ~/site-setup.sh"
Ok "service up on port $Port (enabled at boot)  [server-side script kept at ~/site-setup.sh]"

# ---------------------------------------------------------------- 5. verify online
Step "5/5 verify online"
Assert-Paths

Write-Host @"

============================================================
Published. Send this link to the interviewer:

    $base/

Projects: $(($enabled | ForEach-Object {
    if ($_.kind -eq 'proxy' -and $_.proxyPort) { "http://${ServerIp}:$($_.proxyPort)/" }
    else { "$base/$($_.slug)/" }
}) -join '  ')

Before the interview: turn OFF wifi on your phone, switch to 4G/5G,
and open that link once more.
============================================================
"@ -ForegroundColor Green
