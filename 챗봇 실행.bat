@echo off
rem Career chatbot launcher - double-click to run
cd /d "%~dp0"

rem 1) this folder's own venv, if it exists
set "PY="
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"

rem 2) otherwise borrow the voice chatbot venv (folder under Downloads that has anonymize.py)
if not defined PY for /d %%D in ("%USERPROFILE%\Downloads\*") do if exist "%%D\anonymize.py" if exist "%%D\.venv\Scripts\python.exe" set "PY=%%D\.venv\Scripts\python.exe"

if not defined PY (
    echo [ERROR] Python venv not found.
    pause
    exit /b 1
)
if "%~1"=="--check" (
    echo PY=%PY%
    exit /b 0
)

echo Starting chatbot... the browser will open automatically.
echo To stop: close this window or press Ctrl+C
"%PY%" -m streamlit run app.py
pause
