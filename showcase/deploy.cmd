@echo off
rem One-click publisher for the portfolio site (avoids the .ps1 execution-policy block).
rem The site tree (portal page + every project) is generated from showcase\build\site.json.
rem
rem Usage:
rem   deploy.cmd 123.45.67.89
rem   deploy.cmd 123.45.67.89 8080
rem   deploy.cmd 123.45.67.89 8080 check
rem   deploy.cmd 123.45.67.89 8080 deploy ubuntu
rem
rem Tencent Cloud Linux images use "root" for CentOS-family and "ubuntu" for
rem Ubuntu-family. If root is refused, pass ubuntu as the 4th argument.
setlocal
if "%~1"=="" (
  echo.
  echo   Usage:  deploy.cmd ^<server-public-ip^> [port] [check] [user]
  echo   Example: deploy.cmd 123.45.67.89 8080 deploy ubuntu
  echo.
  pause
  exit /b 1
)
set IP=%~1
set PORT=%~2
if "%PORT%"=="" set PORT=8080
set MODE=
if /i "%~3"=="check" set MODE=-VerifyOnly
set USERARG=
if not "%~4"=="" set USERARG=-User %~4

echo Publishing to %IP%:%PORT%  %USERARG%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build\deploy_to_server.ps1" -ServerIp %IP% -Port %PORT% %USERARG% %MODE%
set RC=%ERRORLEVEL%
echo.
if not "%RC%"=="0" (echo Deploy failed with exit code %RC%) else (echo Deploy finished.)
pause
endlocal
