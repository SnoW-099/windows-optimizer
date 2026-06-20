@echo off
setlocal
set "ROOT=%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py "%ROOT%snow_optimizer.py" %*
    exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%ROOT%snow_optimizer.py" %*
    exit /b %errorlevel%
)

echo Python no esta instalado o no esta en PATH.
echo Instala Python desde https://www.python.org/downloads/ y marca "Add python.exe to PATH".
exit /b 1
