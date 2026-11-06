@echo off
title EEMS Stopper
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop.ps1"
ping 127.0.0.1 -n 3 >nul
