@echo off
title Snow Windows Flow Python - By snow
where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0snow_optimizer.py"
    pause
    exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0snow_optimizer.py"
    pause
    exit /b
)

echo Python no esta instalado o no esta en PATH.
echo Instala Python desde https://www.python.org/downloads/ y marca "Add python.exe to PATH".
pause
