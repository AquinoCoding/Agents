"""
Script principal para executar todo o fluxo do sistema de agentes de IA.
"""

import logging
import os
import sys
from pathlib import Path
import time
import json
import argparse

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.agent_orchestrator import AgentOrchestrator
from src.data_processor import DataProcessor
from src.insight_generator import InsightGenerator
from src.content_generator import ContentGenerator
from src.models.ollama_client import OllamaClient
from src.config.config import OLLAMA_CONFIG

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_news_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_ollama_connection():
    """Verifica a conexão com o Ollama."""
    try:
        client = OllamaClient(OLLAMA_CONFIG)
        models = client.list_models()
        
        if models:
            logger.info(f"Conexão com Ollama estabelecida. Modelos disponíveis: {models}")
            return True
        else:
            logger.warning("Conexão com Ollama estabelecida, mas nenhum modelo encontrado.")
            return False
    except Exception as e:
        logger.error(f"Erro ao conectar com Ollama: {e}")
        return False

def run_data_collection(args):
    """Executa a coleta de dados."""
    logger.info("Iniciando coleta de dados...")
    
    orchestrator = AgentOrchestrator()
    
    if args.agent:
        # Executar apenas um agente específico
        if args.agent not in orchestrator.agents:
            logger.error(f"Agente {args.agent} não encontrado")
            return False
        
        result = orchestrator.run_agent(args.agent)
        success = result.get("success", False)
        
        if success:
            logger.info(f"Coleta de dados do agente {args.agent} concluída com sucesso")
        else:
            logger.error(f"Falha na coleta de dados do agente {args.agent}: {result.get('message', '')}")
        
        return success
    else:
        # Executar todos os agentes
        results = orchestrator.run_all_agents()
        
        # Verificar se pelo menos um agente foi bem-sucedido
        success = any(result.get("success", False) for result in results.values())
        
        if success:
            logger.info("Coleta de dados concluída com sucesso")
        else:
            logger.error("Falha na coleta de dados de todos os agentes")
        
        return success

def run_data_processing():
    """Executa o processamento de dados."""
    logger.info("Iniciando processamento de dados...")
    
    processor = DataProcessor()
    processed_data = processor.process_all_data()
    
    if processed_data:
        logger.info("Processamento de dados concluído com sucesso")
        return True
    else:
        logger.error("Falha no processamento de dados")
        return False

def run_insight_generation():
    """Executa a geração de insights."""
    logger.info("Iniciando geração de insights...")
    
    generator = InsightGenerator()
    insights = generator.generate_all_insights()
    
    if insights:
        logger.info("Geração de insights concluída com sucesso")
        return True
    else:
        logger.error("Falha na geração de insights")
        return False

def run_content_generation(args):
    """Executa a geração de conteúdo."""
    logger.info("Iniciando geração de matérias...")
    
    generator = ContentGenerator()
    articles = generator.generate_all_articles(max_articles=args.max_articles)
    
    if articles:
        logger.info(f"Geração de {len(articles)} matérias concluída com sucesso")
        return True
    else:
        logger.error("Falha na geração de matérias")
        return False

def run_full_pipeline(args):
    """Executa o pipeline completo."""
    logger.info("Iniciando pipeline completo...")
    
    # Verificar conexão com Ollama
    if not check_ollama_connection():
        logger.error("Não foi possível conectar ao Ollama. Verifique se o serviço está em execução.")
        return False
    
    # Coleta de dados
    if not run_data_collection(args):
        logger.error("Falha na etapa de coleta de dados")
        return False
    
    # Processamento de dados
    if not run_data_processing():
        logger.error("Falha na etapa de processamento de dados")
        return False
    
    # Geração de insights
    if not run_insight_generation():
        logger.error("Falha na etapa de geração de insights")
        return False
    
    # Geração de conteúdo
    if not run_content_generation(args):
        logger.error("Falha na etapa de geração de conteúdo")
        return False
    
    logger.info("Pipeline completo executado com sucesso!")
    
    # Exibir resultados
    try:
        with open("data/processed/materias.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"Foram geradas {len(articles)} matérias:")
        for i, article in enumerate(articles, 1):
            logger.info(f"{i}. {article.get('titulo', 'Sem título')} - {article.get('editoria', 'Sem editoria')}")
    
    except Exception as e:
        logger.error(f"Erro ao exibir resultados: {e}")
    
    return True

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Sistema de Agentes de IA para Consumo de Conteúdo")
    
    parser.add_argument("--step", choices=["collect", "process", "insights", "generate", "all"], default="all",
                      help="Etapa específica a ser executada (padrão: all)")
    
    parser.add_argument("--agent", choices=["g1", "twitter", "instagram"], default=None,
                      help="Agente específico para coleta de dados (padrão: todos)")
    
    parser.add_argument("--max-articles", type=int, default=10,
                      help="Número máximo de matérias a serem geradas (padrão: 10)")
    
    args = parser.parse_args()
    
    # Criar diretórios necessários
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/processed/insights", exist_ok=True)
    os.makedirs("data/processed/visualizations", exist_ok=True)
    
    # Executar etapa específica ou pipeline completo
    if args.step == "collect":
        run_data_collection(args)
    elif args.step == "process":
        run_data_processing()
    elif args.step == "insights":
        run_insight_generation()
    elif args.step == "generate":
        run_content_generation(args)
    else:  # all
        run_full_pipeline(args)

if __name__ == "__main__":
    main()
