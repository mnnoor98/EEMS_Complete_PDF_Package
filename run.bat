@echo off
title EEMS Launcher
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch.ps1"
if %errorlevel% neq 0 pause
