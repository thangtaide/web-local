@echo off
setlocal
cd /d "%~dp0.."
py -3 -m app.manager
if errorlevel 1 pause
