#!/bin/bash

echo "========================================"
echo "   Sistema de Obras - Inicializador"
echo "========================================"
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado!"
    echo "Por favor, instale o Python 3.7 ou superior."
    echo "Visite: https://www.python.org/downloads/"
    exit 1
fi

echo "Python encontrado!"
echo

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao criar ambiente virtual!"
        exit 1
    fi
    echo "Ambiente virtual criado com sucesso!"
    echo
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências!"
    exit 1
fi

echo
echo "========================================"
echo "   Iniciando Sistema de Obras..."
echo "========================================"
echo
echo "O sistema será aberto em: http://localhost:5000"
echo "Pressione Ctrl+C para parar o servidor"
echo

# Executar o sistema
python app.py 