@echo off
setlocal
title Crear ZIP - Snow Windows Flow

set "ROOT=%~dp0.."
set "ZIP=%ROOT%\dist\Snow-Windows-Flow-By-snow.zip"

if not exist "%ROOT%\dist" mkdir "%ROOT%\dist"

if exist "%ZIP%" del "%ZIP%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%ROOT%\src','%ROOT%\scripts','%ROOT%\snow.cmd','%ROOT%\Abrir Snow Optimizer Python.bat','%ROOT%\Abrir Snow Optimizer Python Admin.bat','%ROOT%\instalar_comando_snow.bat','%ROOT%\README.md' -DestinationPath '%ZIP%' -Force"

echo.
echo ZIP creado:
echo %ZIP%
echo.
pause
