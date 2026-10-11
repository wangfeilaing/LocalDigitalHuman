# Build installer/staging (slim package payload).
# Usage: powershell -ExecutionPolicy Bypass -File installer\build-staging.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$staging = Join-Path $PSScriptRoot 'staging'
$hdSource = 'C:\Program Files\aigc-human\python-modules\hdModule'
$ffmpegSource = 'C:\Program Files\aigc-human\resources\ffmpeg\bin'

if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path $staging | Out-Null

# ---- app code (runtime files only; no temp/logs/backups/personal assets) ----
$codeFiles = @(
  'server.py', 'app.js', 'index.html', 'styles.css', 'ui-fx.js',
  'model_worker.py', 'voxcpm_service.py', 'sitecustomize.py',
  'broll_classifier.py', 'broll_matcher.py'
)
foreach ($f in $codeFiles) { Copy-Item (Join-Path $root $f) $staging }
# The launcher has a Chinese file name; PS 5.1 misreads non-ASCII literals in
# a BOM-less script, so copy it via an ASCII wildcard instead.
Copy-Item (Join-Path $root '*.vbs') $staging
if (-not (Get-ChildItem $staging -Filter '*.vbs' -File)) { throw "launcher .vbs missing from staging" }
Copy-Item (Join-Path $root 'tools') (Join-Path $staging 'tools') -Recurse
Copy-Item (Join-Path $root 'assets') (Join-Path $staging 'assets') -Recurse
New-Item -ItemType Directory -Path (Join-Path $staging 'data\fonts') -Force | Out-Null
Copy-Item (Join-Path $root 'data\fonts\*') (Join-Path $staging 'data\fonts') -Recurse

# ---- embeddable Python (runs server.py) ----
$embedZip = Join-Path $PSScriptRoot 'python-embed.zip'
if (-not (Test-Path $embedZip)) { throw "missing $embedZip (download embeddable zip from python.org first)" }
$embedDir = Join-Path $staging 'runtime\python'
Expand-Archive $embedZip $embedDir

# Cover generation needs Pillow + OpenCV + numpy inside the embedded runtime.
# Enable site-packages in the ._pth, bootstrap pip, then install the wheels.
$pth = Get-ChildItem $embedDir -Filter '*._pth' | Select-Object -First 1
Add-Content $pth.FullName "Lib\site-packages"
Add-Content $pth.FullName "import site"
$getPip = Join-Path $env:TEMP 'get-pip.py'
if (-not (Test-Path $getPip)) {
  Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile $getPip
}
& (Join-Path $embedDir 'python.exe') $getPip --no-warn-script-location -i https://pypi.tuna.tsinghua.edu.cn/simple
if ($LASTEXITCODE -ne 0) { throw "get-pip failed (exit $LASTEXITCODE)" }
# Pin opencv to 4.12: 5.x removed cv2.CascadeClassifier which the cover generator uses.
& (Join-Path $embedDir 'python.exe') -m pip install --no-warn-script-location pillow "opencv-python-headless==4.12.0.88" -i https://pypi.tuna.tsinghua.edu.cn/simple
if ($LASTEXITCODE -ne 0) { throw "pip install cover deps failed (exit $LASTEXITCODE)" }
# pip itself is only needed at build time; keep it (small) so future fixes are possible.

# ---- VC++ runtime DLLs (app-local; target machine needs no redist install) ----
# Fresh Windows lacks VC++ 2015-2022 runtimes that torch/onnxruntime/opencv need,
# and an old/broken redist can block installing a new one. Shipping the DLLs
# inside the package sidesteps the system entirely.
$vcDlls = @(
  'vcruntime140.dll', 'vcruntime140_1.dll', 'vcruntime140_threads.dll',
  'msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll',
  'msvcp140_atomic_wait.dll', 'msvcp140_codecvt_ids.dll',
  'concrt140.dll', 'vccorlib140.dll'
)
$vcTarget = Join-Path $staging 'runtime\vcredist'
New-Item -ItemType Directory -Path $vcTarget -Force | Out-Null
foreach ($dll in $vcDlls) {
  $src = "C:\Windows\System32\$dll"
  if (-not (Test-Path $src)) { throw "missing VC++ runtime dll: $src" }
  Copy-Item $src $vcTarget
  Copy-Item $src $embedDir
}

# ---- ffmpeg ----
Copy-Item $ffmpegSource (Join-Path $staging 'runtime\ffmpeg\bin') -Recurse

# ---- lip-sync v2 module (hdModule): code + checkpoints, no venv/temp ----
$hdTarget = Join-Path $staging 'modules\hdModule'
robocopy $hdSource $hdTarget /E /XD venv temp outputs __pycache__ build /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -gt 7) { throw "robocopy hdModule failed (exit $LASTEXITCODE)" }

Write-Output "staging done: $staging"
