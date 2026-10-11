param(
    [string]$InitialPath = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$owner = New-Object System.Windows.Forms.Form
$owner.Text = "选择视频保存位置"
$owner.StartPosition = "CenterScreen"
$owner.Size = New-Object System.Drawing.Size(1, 1)
$owner.ShowInTaskbar = $false
$owner.TopMost = $true
$owner.Opacity = 0

$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "选择数字人视频保存文件夹"
$dialog.ShowNewFolderButton = $true
if ($InitialPath -and (Test-Path -LiteralPath $InitialPath -PathType Container)) {
    $dialog.SelectedPath = [System.IO.Path]::GetFullPath($InitialPath)
}

try {
    $owner.Show()
    $owner.Activate()
    if ($dialog.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) {
        [Console]::Write([System.IO.Path]::GetFullPath($dialog.SelectedPath))
    }
}
finally {
    $dialog.Dispose()
    $owner.Close()
    $owner.Dispose()
}
