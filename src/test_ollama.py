"""
Script principal para testar a conexão com o Ollama.
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.ollama_client import OllamaClient
from src.config.config import OLLAMA_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ollama_connection():
    """Testa a conexão com o Ollama e verifica se o modelo está disponível."""
    try:
        # Inicializar o cliente Ollama
        client = OllamaClient(OLLAMA_CONFIG)
        
        # Listar modelos disponíveis
        available_models = client.list_models()
        logger.info(f"Modelos disponíveis: {available_models}")
        
        # Verificar se o modelo configurado está disponível
        model_name = OLLAMA_CONFIG.get("model", "gemma")
        if model_name in available_models:
            logger.info(f"Modelo {model_name} está disponível!")
            
            # Testar geração de texto
            test_prompt = "Olá, estou testando a conexão com o Ollama. Por favor, responda com uma frase curta."
            response = client.generate(test_prompt, max_tokens=50)
            logger.info(f"Resposta do modelo: {response}")
            
            return True, "Conexão com Ollama estabelecida com sucesso!"
        else:
            logger.warning(f"Modelo {model_name} não está disponível. Modelos disponíveis: {available_models}")
            
            if available_models:
                logger.info(f"Tentando usar o primeiro modelo disponível: {available_models[0]}")
                client.change_model(available_models[0])
                
                # Testar geração de texto com o modelo alternativo
                test_prompt = "Olá, estou testando a conexão com o Ollama. Por favor, responda com uma frase curta."
                response = client.generate(test_prompt, max_tokens=50)
                logger.info(f"Resposta do modelo alternativo: {response}")
                
                return True, f"Conexão estabelecida com modelo alternativo: {available_models[0]}"
            else:
                return False, "Nenhum modelo disponível no Ollama."
    
    except Exception as e:
        logger.error(f"Erro ao conectar com Ollama: {e}")
        return False, f"Erro na conexão com Ollama: {str(e)}"

if __name__ == "__main__":
    logger.info("Testando conexão com Ollama...")
    success, message = test_ollama_connection()
    
    if success:
        logger.info(f"Teste concluído com sucesso: {message}")
        sys.exit(0)
    else:
        logger.error(f"Teste falhou: {message}")
        logger.info("Verifique se o Ollama está instalado e em execução com o comando: 'ollama serve'")
        sys.exit(1)
