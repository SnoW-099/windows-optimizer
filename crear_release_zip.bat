@echo off
setlocal
title Crear ZIP - Snow Windows Flow

set "ROOT=%~dp0"
set "ZIP=%ROOT%Snow-Windows-Flow-By-snow.zip"

if exist "%ZIP%" del "%ZIP%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%ROOT%snow_optimizer.py','%ROOT%snow.cmd','%ROOT%Abrir Snow Optimizer Python.bat','%ROOT%Abrir Snow Optimizer Python Admin.bat','%ROOT%instalar_comando_snow.bat','%ROOT%crear_release_zip.bat','%ROOT%README.md' -DestinationPath '%ZIP%' -Force"

echo.
echo ZIP creado:
echo %ZIP%
echo.
pause
