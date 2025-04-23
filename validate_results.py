"""
Script para validar os resultados do sistema de agentes de IA.
"""

import logging
import json
import os
from pathlib import Path
import sys
import argparse

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.models.ollama_client import OllamaClient
from src.config.config import OLLAMA_CONFIG

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResultValidator:
    """Validador de resultados do sistema de agentes de IA."""
    
    def __init__(self):
        """Inicializa o validador de resultados."""
        self.ollama_client = OllamaClient(OLLAMA_CONFIG)
        logger.info("Validador de resultados inicializado")
    
    def validate_article_format(self, article: dict) -> dict:
        """
        Valida o formato de uma matéria.
        
        Args:
            article: Matéria a ser validada
            
        Returns:
            Resultado da validação
        """
        required_fields = ["materia", "editoria", "subtitulo", "titulo", "keywords"]
        missing_fields = [field for field in required_fields if field not in article]
        
        # Verificar campos obrigatórios
        if missing_fields:
            return {
                "valid": False,
                "message": f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
                "article": article
            }
        
        # Verificar conteúdo da matéria
        if not article.get("materia", ""):
            return {
                "valid": False,
                "message": "Conteúdo da matéria está vazio",
                "article": article
            }
        
        # Verificar número de palavras
        word_count = len(article.get("materia", "").split())
        if word_count < 500:
            return {
                "valid": False,
                "message": f"Matéria tem apenas {word_count} palavras (mínimo: 500)",
                "article": article
            }
        
        # Verificar número de parágrafos
        paragraphs = article.get("materia", "").split("\n\n")
        if len(paragraphs) > 5:
            return {
                "valid": False,
                "message": f"Matéria tem {len(paragraphs)} parágrafos (máximo: 5)",
                "article": article
            }
        
        # Verificar presença de aspas
        if '"' in article.get("materia", "") or "'" in article.get("materia", ""):
            return {
                "valid": False,
                "message": "Matéria contém aspas",
                "article": article
            }
        
        # Verificar keywords
        if not isinstance(article.get("keywords", []), list) or len(article.get("keywords", [])) == 0:
            return {
                "valid": False,
                "message": "Keywords ausentes ou em formato inválido",
                "article": article
            }
        
        return {
            "valid": True,
            "message": "Matéria válida",
            "article": article,
            "word_count": word_count,
            "paragraph_count": len(paragraphs)
        }
    
    def validate_articles_file(self, file_path: str) -> dict:
        """
        Valida um arquivo de matérias.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Resultado da validação
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "message": f"Arquivo não encontrado: {file_path}",
                    "articles": []
                }
            
            # Carregar arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            # Verificar se é uma lista
            if not isinstance(articles, list):
                return {
                    "valid": False,
                    "message": "Formato inválido: o arquivo deve conter uma lista de matérias",
                    "articles": []
                }
            
            # Validar cada matéria
            validation_results = [self.validate_article_format(article) for article in articles]
            
            # Contar matérias válidas e inválidas
            valid_count = sum(1 for result in validation_results if result["valid"])
            invalid_count = len(validation_results) - valid_count
            
            return {
                "valid": valid_count > 0,
                "message": f"{valid_count} matérias válidas, {invalid_count} inválidas",
                "total_articles": len(articles),
                "valid_articles": valid_count,
                "invalid_articles": invalid_count,
                "validation_results": validation_results
            }
        
        except Exception as e:
            logger.error(f"Erro ao validar arquivo de matérias: {e}")
            return {
                "valid": False,
                "message": f"Erro ao validar arquivo: {str(e)}",
                "articles": []
            }
    
    def validate_insights_file(self, file_path: str) -> dict:
        """
        Valida um arquivo de insights.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Resultado da validação
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "message": f"Arquivo não encontrado: {file_path}",
                    "insights": {}
                }
            
            # Carregar arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                insights = json.load(f)
            
            # Verificar se é um dicionário
            if not isinstance(insights, dict):
                return {
                    "valid": False,
                    "message": "Formato inválido: o arquivo deve conter um dicionário de insights",
                    "insights": {}
                }
            
            # Verificar campos obrigatórios
            required_fields = ["source_distribution", "topic_insights", "engagement_metrics", "content_recommendations"]
            missing_fields = [field for field in required_fields if field not in insights]
            
            if missing_fields:
                return {
                    "valid": False,
                    "message": f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
                    "insights": insights
                }
            
            return {
                "valid": True,
                "message": "Arquivo de insights válido",
                "insights": insights,
                "topic_count": len(insights.get("topic_insights", [])),
                "recommendation_count": len(insights.get("content_recommendations", []))
            }
        
        except Exception as e:
            logger.error(f"Erro ao validar arquivo de insights: {e}")
            return {
                "valid": False,
                "message": f"Erro ao validar arquivo: {str(e)}",
                "insights": {}
            }
    
    def validate_all_results(self) -> dict:
        """
        Valida todos os resultados do sistema.
        
        Returns:
            Resultado da validação
        """
        # Validar arquivo de matérias
        articles_result = self.validate_articles_file("data/processed/materias.json")
        
        # Validar arquivo de insights
        insights_result = self.validate_insights_file("data/processed/insights.json")
        
        # Verificar existência de visualizações
        visualization_files = list(Path("data/processed/visualizations").glob("*.png"))
        visualizations_valid = len(visualization_files) > 0
        
        # Consolidar resultados
        all_valid = articles_result["valid"] and insights_result["valid"] and visualizations_valid
        
        return {
            "valid": all_valid,
            "message": "Validação concluída",
            "articles_validation": articles_result,
            "insights_validation": insights_result,
            "visualizations_valid": visualizations_valid,
            "visualization_count": len(visualization_files)
        }

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Validador de Resultados do Sistema de Agentes de IA")
    
    parser.add_argument("--articles", action="store_true", help="Validar apenas o arquivo de matérias")
    parser.add_argument("--insights", action="store_true", help="Validar apenas o arquivo de insights")
    parser.add_argument("--all", action="store_true", help="Validar todos os resultados (padrão)")
    
    args = parser.parse_args()
    
    validator = ResultValidator()
    
    if args.articles:
        result = validator.validate_articles_file("data/processed/materias.json")
        logger.info(f"Validação de matérias: {result['message']}")
        
        if result["valid"]:
            logger.info("Detalhes das matérias válidas:")
            for i, validation in enumerate(result["validation_results"]):
                if validation["valid"]:
                    article = validation["article"]
                    logger.info(f"{i+1}. {article.get('titulo', 'Sem título')} - {validation.get('word_count', 0)} palavras, {validation.get('paragraph_count', 0)} parágrafos")
    
    elif args.insights:
        result = validator.validate_insights_file("data/processed/insights.json")
        logger.info(f"Validação de insights: {result['message']}")
        
        if result["valid"]:
            logger.info(f"Tópicos encontrados: {result.get('topic_count', 0)}")
            logger.info(f"Recomendações geradas: {result.get('recommendation_count', 0)}")
    
    else:  # all
        result = validator.validate_all_results()
        logger.info(f"Validação completa: {'Sucesso' if result['valid'] else 'Falha'}")
        logger.info(f"Matérias: {result['articles_validation']['message']}")
        logger.info(f"Insights: {result['insights_validation']['message']}")
        logger.info(f"Visualizações: {'Válidas' if result['visualizations_valid'] else 'Inválidas'} ({result['visualization_count']} encontradas)")

if __name__ == "__main__":
    main()
