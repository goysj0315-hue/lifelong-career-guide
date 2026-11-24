@echo off
chcp 65001 >nul
rem Career chatbot launcher - double-click to run
rem For now it borrows the venv from the voice chatbot folder (no install needed)
cd /d "%~dp0"
set PY=%USERPROFILE%\Downloads\학생 음성 인식 챗봇\.venv\Scripts\python.exe
if exist ".venv\Scripts\python.exe" set PY=.venv\Scripts\python.exe
echo Starting chatbot... the browser will open automatically.
echo To stop: close this window or press Ctrl+C
"%PY%" -m streamlit run app.py
pause
