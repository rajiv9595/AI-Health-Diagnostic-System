@echo off
REM Enable UTF-8 encoding for Windows console
chcp 65001 > nul

echo ============================================================
echo AI Health Diagnostic System - Model Training
echo ============================================================
echo.

python train_models.py

pause










