@echo off
chcp 65001 > nul
title EEMS Backend API [Port 5131]
cd /d "%~dp0..\backend"
echo ============================================================
echo   Starting EEMS Backend API on http://localhost:5131
echo ============================================================
dotnet run --project src/EEMS.Api
echo.
echo Backend API has stopped.
pause

