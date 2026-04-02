@echo off
chcp 65001 >nul
set "SRC=%~dp0"
set "DEST=%USERPROFILE%\second-brain-pipeline"
set "PY=C:\Program Files\Python313\python.exe"

echo.
echo === Second Brain Pipeline - Instalador ===
echo SRC: %SRC%
echo DEST: %DEST%
echo.

:: 1. Criar pasta destino
if not exist "%DEST%" mkdir "%DEST%"

:: 2. Copiar arquivos um por um
echo [1/4] Copiando arquivos...
copy /Y "%SRC%pipeline.py"      "%DEST%\pipeline.py"
copy /Y "%SRC%config.json"      "%DEST%\config.json"
copy /Y "%SRC%requirements.txt" "%DEST%\requirements.txt"
copy /Y "%SRC%agendar.ps1"      "%DEST%\agendar.ps1"
copy /Y "%SRC%README.md"        "%DEST%\README.md"

if not exist "%DEST%\pipeline.py" (
    echo ERRO: copia falhou. Verifique permissoes.
    pause & exit /b 1
)
echo   OK

:: 3. Instalar dependencias
echo [2/4] Instalando dependencias Python...
"%PY%" -m pip install feedparser anthropic requests -q
echo   OK

:: 4. Agendar tarefas
echo [3/4] Agendando tarefas (08h e 17h)...
powershell -ExecutionPolicy Bypass -File "%DEST%\agendar.ps1"

:: 5. Dry-run
echo.
echo [4/4] Testando pipeline (dry-run)...
echo ==========================================
"%PY%" "%DEST%\pipeline.py" --dry-run

echo.
echo === CONCLUIDO! Pasta: %DEST% ===
echo.
pause
