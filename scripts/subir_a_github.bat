@echo off
setlocal
title Subir Windows Optimizer a GitHub

set "ROOT=%~dp0.."
pushd "%ROOT%"

echo.
echo Windows Optimizer - subir a GitHub
echo By snow
echo.

where git >nul 2>nul
if not %errorlevel%==0 (
    echo Git no esta instalado o no esta en PATH.
    echo.
    echo Instala Git for Windows desde:
    echo https://git-scm.com/download/win
    echo.
    echo Luego vuelve a abrir este archivo.
    pause
    exit /b 1
)

set /p REPO_URL=Pega la URL del repo GitHub, por ejemplo https://github.com/usuario/windows-optimizer.git: 

if "%REPO_URL%"=="" (
    echo No se puso ninguna URL.
    pause
    exit /b 1
)

git remote remove origin >nul 2>nul
git remote add origin "%REPO_URL%"
git branch -M main
git push -u origin main

echo.
echo Si no hubo errores, ya deberia verse en GitHub.
popd
pause
