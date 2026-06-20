@echo off
title Snow Windows Flow Python - By snow
set "APP=%~dp0src\snow_optimizer.py"
where py >nul 2>nul
if %errorlevel%==0 (
    py "%APP%"
    pause
    exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%APP%"
    pause
    exit /b
)

echo Python no esta instalado o no esta en PATH.
echo Instala Python desde https://www.python.org/downloads/ y marca "Add python.exe to PATH".
pause
