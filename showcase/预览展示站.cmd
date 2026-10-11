@echo off
rem Preview the static showcase site locally.
rem Serves this folder on http://127.0.0.1:8080/ and opens the browser.
setlocal
set PORT=8080
rem %~dp0 ends with a backslash, which would escape the closing quote in the
rem --directory argument below, so strip it.
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

start "" "http://127.0.0.1:%PORT%/"
echo Serving %ROOT% on http://127.0.0.1:%PORT%/  (Ctrl+C to stop)
python -m http.server %PORT% --directory "%ROOT%"
endlocal
