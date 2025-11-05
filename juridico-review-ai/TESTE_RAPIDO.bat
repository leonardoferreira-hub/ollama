@echo off
REM Script para teste rápido do validador CRI
REM Windows Batch Script

echo ============================================================
echo     VALIDADOR DOCUMENTAL CRI - TESTE RAPIDO
echo ============================================================
echo.

echo [1/3] Verificando instalacao...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/3] Instalando dependencias (se necessario)...
pip install -q -r requirements.txt

echo.
echo [3/3] Iniciando interface web...
echo.
echo ============================================================
echo   App estara disponivel em: http://localhost:8501
echo   Pressione Ctrl+C para encerrar
echo ============================================================
echo.

streamlit run app_streamlit.py

pause
