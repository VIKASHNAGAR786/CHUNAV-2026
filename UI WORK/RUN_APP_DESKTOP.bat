@echo off
chcp 65001 > nul
title JAINAGAR CHUNAV 2026 - OFFLINE MOBILE APP (DESKTOP)
cd /d "%~dp0"

echo =====================================================================
echo            JAINAGAR CHUNAV 2026 - OFFLINE MOBILE APP
echo            Candidate: Pradhyumna Nagar (प्रद्युम्न नागर)
echo            Post: Sarpanch (सरपंच पद हेतु) - Gram Panchayat Jayanagar
echo =====================================================================
echo.
echo [1/2] Checking Python & pywebview...
python -c "import webview" 2>nul
if %errorlevel% neq 0 (
    echo [!] Installing required pywebview package for crystal-clear Hindi...
    pip install pywebview
)

echo [2/2] Launching Mobile App with Crystal-Clear Devanagari Hindi font...
echo.
python app.py
pause
