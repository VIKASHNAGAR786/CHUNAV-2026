@echo off
chcp 65001 > nul
title JAINAGAR CHUNAV 2026 - OPEN IN BROWSER
cd /d "%~dp0"

echo =====================================================================
echo            JAINAGAR CHUNAV 2026 - 100%% OFFLINE WEB APP
echo            Candidate: Pradhyumna Nagar (प्रद्युम्न नागर)
echo            Post: Sarpanch (सरपंच पद) - Gram Panchayat Jayanagar
echo =====================================================================
echo.
echo Opening 100%% Offline Voter App in your default Browser (Edge/Chrome)...
start "" "%~dp0www\index.html"
