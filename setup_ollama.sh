#!/bin/bash

# Script para instalar o Ollama e baixar o modelo Gemma
# Autor: Manus AI
# Data: 23/04/2025

echo "Instalando o Ollama..."

# Verificar se o Ollama já está instalado
if command -v ollama &> /dev/null; then
    echo "Ollama já está instalado."
else
    # Instalar o Ollama
    curl -fsSL https://ollama.com/install.sh | sh
    
    if [ $? -ne 0 ]; then
        echo "Erro ao instalar o Ollama. Por favor, verifique a conexão com a internet e tente novamente."
        exit 1
    fi
    
    echo "Ollama instalado com sucesso."
fi

# Iniciar o serviço Ollama
echo "Iniciando o serviço Ollama..."
ollama serve &

# Aguardar o serviço iniciar
sleep 5

# Baixar o modelo Gemma
echo "Baixando o modelo Gemma..."
ollama pull gemma

if [ $? -ne 0 ]; then
    echo "Erro ao baixar o modelo Gemma. Por favor, verifique a conexão com a internet e tente novamente."
    exit 1
fi

echo "Modelo Gemma baixado com sucesso."
echo "Configuração concluída! O Ollama está em execução e o modelo Gemma está disponível."
echo "Para usar o sistema de agentes de IA, execute: python main.py"
