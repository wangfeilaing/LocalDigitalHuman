Option Explicit

Dim shell, fso, scriptDir, serverScript, pythonExe, edgeExe, appUrl, isRunning, request
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
serverScript = fso.BuildPath(scriptDir, "server.py")
appUrl = "http://127.0.0.1:17860"

pythonExe = fso.BuildPath(scriptDir, "runtime\python\pythonw.exe")
If Not fso.FileExists(pythonExe) Then
  pythonExe = fso.BuildPath(scriptDir, "modules\voiceV2Module\venv\pythonw.exe")
End If
If Not fso.FileExists(pythonExe) Then
  MsgBox "Local model runtime was not found.", 16, "Local Digital Human"
  WScript.Quit 1
End If

isRunning = False
On Error Resume Next
Set request = CreateObject("WinHttp.WinHttpRequest.5.1")
request.SetTimeouts 300, 300, 500, 500
request.Open "GET", appUrl & "/api/ping", False
request.Send
If Err.Number = 0 Then
  If request.Status = 200 Then isRunning = True
End If
Err.Clear
On Error GoTo 0

If Not isRunning Then
  shell.CurrentDirectory = scriptDir
  shell.Run Chr(34) & pythonExe & Chr(34) & " " & Chr(34) & serverScript & Chr(34), 0, False
  WScript.Sleep 1800
End If

edgeExe = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
If Not fso.FileExists(edgeExe) Then
  edgeExe = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
End If

If fso.FileExists(edgeExe) Then
  shell.Run Chr(34) & edgeExe & Chr(34) & " --app=" & appUrl & " --start-maximized", 1, False
Else
  shell.Run appUrl, 1, False
End If
