@echo off
chcp 65001 > nul
title JAINAGAR CHUNAV 2026 - MOBILE APP (DESKTOP PREVIEW)
cd /d "%~dp0"

echo =====================================================================
echo            JAINAGAR CHUNAV 2026 - OFFLINE MOBILE APP
echo            Candidate: Pradhyumna Nagar (प्रद्युम्न नागर)
echo =====================================================================
echo.
echo Launching Mobile App Preview on your Desktop...
echo.
python main.py
pause
