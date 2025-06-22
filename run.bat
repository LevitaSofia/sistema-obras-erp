@echo off
echo ========================================
echo    Sistema de Obras - Inicializador
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.7 ou superior.
    echo Visite: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso!
    echo.
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Iniciando Sistema de Obras...
echo ========================================
echo.
echo O sistema sera aberto em: http://localhost:5000
echo Pressione Ctrl+C para parar o servidor
echo.

REM Executar o sistema
python app.py

pause 