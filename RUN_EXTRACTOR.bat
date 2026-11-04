@echo off
chcp 65001 > nul
title SMART VOTER LIST TO EXCEL EXTRACTOR

:MENU
cls
echo =====================================================================
echo           SMART VOTER LIST PDF TO EXCEL EXTRACTOR (RAJASTHAN)
echo =====================================================================
echo.
echo  [1] Process ALL 9 PDFs in "VOTER LISTS" folder (Batch Mode)
echo  [2] Process a Single PDF file
echo  [3] Run Diagnostic and Synthetic Tests
echo  [4] Open Output Folder
echo  [5] Exit
echo.
echo =====================================================================
set /p choice="Select an option (1-5): "

if "%choice%"=="1" goto BATCH
if "%choice%"=="2" goto SINGLE
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto OPEN_FOLDER
if "%choice%"=="5" goto EXIT
goto MENU

:BATCH
cls
echo Starting Batch Processing for all PDFs in "VOTER LISTS"...
echo.
python batch_process_all.py
echo.
pause
goto MENU

:SINGLE
cls
echo.
echo Drag and drop your PDF file here, or enter its full path:
set /p user_pdf="PDF File Path: "
cls
echo Processing %user_pdf% ...
echo.
python voter_pdf_to_excel.py %user_pdf%
echo.
pause
goto MENU

:TEST
cls
echo Running synthetic test suite...
echo.
python test_synthetic_pipeline.py
echo.
pause
goto MENU

:OPEN_FOLDER
explorer output
goto MENU

:EXIT
exit
