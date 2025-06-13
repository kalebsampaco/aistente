@echo off
title Iniciar IA Asistente

REM Activar entorno virtual
cd /d "%~dp0"
call ..\Scripts\activate.bat

REM Iniciar Ollama si no está corriendo
echo Verificando estado de Ollama...
tasklist | findstr /i "ollama" >nul
if errorlevel 1 (
    echo Iniciando servidor Ollama...
    start /B ollama serve
    timeout /t 5
) else (
    echo Ollama ya está corriendo.
)

REM Ejecutar FastAPI con Uvicorn
echo Iniciando FastAPI...
start cmd /k "python -m app.main"
