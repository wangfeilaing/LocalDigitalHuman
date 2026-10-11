$procs = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' or Name='python.exe'" | Where-Object { $_.CommandLine -match 'server\.py' }
$procs | Select-Object ProcessId, Name | Format-Table -AutoSize
foreach ($p in $procs) {
  Stop-Process -Id $p.ProcessId -Force
  Write-Output ("stopped " + $p.ProcessId)
}
Start-Sleep -Milliseconds 800
$py = "D:\LocalDigitalHuman\modules\voiceV2Module\venv\pythonw.exe"
$workdir = "D:\LocalDigitalHuman"
Start-Process -FilePath $py -ArgumentList "`"$workdir\server.py`"" -WorkingDirectory $workdir -WindowStyle Hidden
Write-Output "restarted"
