@echo off
chcp 65001 >nul
title EKHO

python "%~dp0app.py"
pause
