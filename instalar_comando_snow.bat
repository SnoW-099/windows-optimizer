@echo off
setlocal EnableExtensions
title Instalar comando snow - By snow

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"

echo.
echo Snow Windows Flow - instalador de terminal
echo By snow
echo.
echo Carpeta: %APP_DIR%
echo.

where py >nul 2>nul
if %errorlevel%==0 goto python_ok

where python >nul 2>nul
if %errorlevel%==0 goto python_ok

echo Python no esta instalado o no esta en PATH.
echo Instala Python desde https://www.python.org/downloads/
echo Importante: marca "Add python.exe to PATH".
echo.
pause
exit /b 1

:python_ok
echo Python detectado.
echo.

echo Agregando esta carpeta al PATH de usuario...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$dir='%APP_DIR%'; $old=[Environment]::GetEnvironmentVariable('Path','User'); if(($old -split ';') -notcontains $dir){ [Environment]::SetEnvironmentVariable('Path', (($old.TrimEnd(';') + ';' + $dir).Trim(';')), 'User'); Write-Host 'OK: PATH actualizado.' } else { Write-Host 'OK: ya estaba instalado.' }"

echo.
echo Listo. Cierra y abre una terminal nueva, luego escribe:
echo.
echo     snow
echo.
pause
