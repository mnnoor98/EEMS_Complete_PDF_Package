@echo off
chcp 65001 > nul
title EEMS Frontend Angular [Port 4200]
cd /d "%~dp0..\frontend"
echo ============================================================
echo   Starting EEMS Frontend on http://localhost:4200
echo ============================================================
npm start
echo.
echo Frontend server has stopped.
pause

