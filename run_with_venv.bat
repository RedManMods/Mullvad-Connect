@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=!SCRIPT_DIR:YOUR_FOLDER_NAME_HERE=!"
set venv="YOUR_VENV_NAME_HERE"

call "!SCRIPT_DIR!\!venv!\Scripts\activate.bat"
python mullvad_connect.py
rem cmd /K
endlocal
