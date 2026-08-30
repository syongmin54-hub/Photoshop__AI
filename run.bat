@echo off
chcp 65001 > nul
title Adobe AI Controller (Photoshop & Illustrator)

echo ========================================================
echo   🎨 Adobe AI Controller 실행 중...
echo ========================================================

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org 에서 Python을 설치해 주세요.
    pause
    exit /b
)

REM Install dependencies if needed
if not exist "venv" (
    echo [안내] 최초 1회 실행 환경을 구성 중입니다...
    python -m venv venv
    call venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

REM Run Main CLI
python main.py

pause
