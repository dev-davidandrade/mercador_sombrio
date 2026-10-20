@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Criando ambiente virtual...
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
  if errorlevel 1 goto erro
)
if not exist ".venv\.instalado" (
  echo [2/3] Instalando dependencias (requer internet)...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto erro
  type nul > ".venv\.instalado"
)
echo [3/3] Abrindo Mercador Sombrio...
echo Acesse http://127.0.0.1:8000
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
goto fim
:erro
echo Nao foi possivel iniciar. Verifique se Python 3.11+ esta instalado e conectado a internet.
pause
:fim
endlocal
