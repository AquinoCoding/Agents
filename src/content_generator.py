"""
Gerador de matérias em formato JSON a partir dos dados processados e insights.
"""

import logging
import json
from typing import List, Dict, Any
import os
from pathlib import Path
import sys
from datetime import datetime
import random

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.ollama_client import OllamaClient
from src.config.config import OLLAMA_CONFIG, CONTENT_GENERATION_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentGenerator:
    """Gerador de matérias em formato JSON a partir dos dados processados e insights."""
    
    def __init__(self):
        """Inicializa o gerador de conteúdo."""
        self.min_words = CONTENT_GENERATION_CONFIG.get("min_words", 500)
        self.max_paragraphs = CONTENT_GENERATION_CONFIG.get("max_paragraphs", 5)
        self.temperature = CONTENT_GENERATION_CONFIG.get("temperature", 0.7)
        self.top_p = CONTENT_GENERATION_CONFIG.get("top_p", 0.9)
        
        # Inicializar cliente Ollama
        self.ollama_client = OllamaClient(OLLAMA_CONFIG)
        
        # Criar diretório para saída
        os.makedirs("data/processed", exist_ok=True)
        
        logger.info("Gerador de conteúdo inicializado")
    
    def load_insights(self) -> Dict[str, Any]:
        """
        Carrega os insights gerados.
        
        Returns:
            Insights gerados
        """
        file_path = "data/processed/insights.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Insights carregados de {file_path}")
            return data
        except Exception as e:
            logger.error(f"Erro ao carregar insights: {e}")
            return {}
    
    def load_consolidated_data(self) -> Dict[str, Any]:
        """
        Carrega os dados consolidados.
        
        Returns:
            Dados consolidados
        """
        file_path = "data/processed/consolidated_data.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Dados consolidados carregados de {file_path}")
            return data
        except Exception as e:
            logger.error(f"Erro ao carregar dados consolidados: {e}")
            return {}
    
    def generate_article(self, topic: str, facts: List[str], editoria: str = None) -> Dict[str, Any]:
        """
        Gera uma matéria sobre um tópico.
        
        Args:
            topic: Tópico da matéria
            facts: Fatos relevantes sobre o tópico
            editoria: Editoria da matéria (opcional)
            
        Returns:
            Matéria gerada em formato JSON
        """
        try:
            # Determinar editoria se não fornecida
            if not editoria:
                editorias = ["Política", "Economia", "Entretenimento", "Tecnologia", "Esportes", "Saúde", "Educação", "Mundo"]
                editoria = random.choice(editorias)
            
            # Gerar matéria usando o cliente Ollama
            article_data = self.ollama_client.generate_article(
                topic=topic,
                facts=facts,
                min_words=self.min_words,
                max_paragraphs=self.max_paragraphs
            )
            
            # Garantir que a editoria está definida
            if not article_data.get("editoria"):
                article_data["editoria"] = editoria
            
            # Adicionar metadados
            article_data["generated_at"] = datetime.now().isoformat()
            
            logger.info(f"Matéria gerada sobre o tópico '{topic}'")
            return article_data
        
        except Exception as e:
            logger.error(f"Erro ao gerar matéria sobre o tópico '{topic}': {e}")
            return {
                "materia": f"Não foi possível gerar a matéria sobre {topic} devido a um erro: {str(e)}",
                "titulo": f"Erro na geração de matéria sobre {topic}",
                "subtitulo": "Falha no processamento",
                "editoria": editoria or "Geral",
                "keywords": [topic, "erro", "falha"],
                "generated_at": datetime.now().isoformat()
            }
    
    def generate_articles_from_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Gera matérias a partir das recomendações.
        
        Args:
            recommendations: Lista de recomendações de conteúdo
            
        Returns:
            Lista de matérias geradas
        """
        articles = []
        
        for recommendation in recommendations:
            topic = recommendation.get("topic", "")
            facts = recommendation.get("key_facts", [])
            priority = recommendation.get("priority", "Média")
            
            # Gerar apenas para recomendações de alta prioridade ou algumas de média prioridade
            if priority == "Alta" or (priority == "Média" and random.random() > 0.5):
                article = self.generate_article(topic, facts)
                articles.append(article)
        
        logger.info(f"Geradas {len(articles)} matérias a partir das recomendações")
        return articles
    
    def generate_articles_from_trending_topics(self, topic_insights: List[Dict[str, Any]], max_articles: int = 5) -> List[Dict[str, Any]]:
        """
        Gera matérias a partir dos tópicos em tendência.
        
        Args:
            topic_insights: Lista de insights sobre tópicos
            max_articles: Número máximo de artigos a gerar
            
        Returns:
            Lista de matérias geradas
        """
        articles = []
        
        # Ordenar tópicos por pontuação de tendência
        sorted_topics = sorted(topic_insights, key=lambda x: x.get("trend_score", 0), reverse=True)
        
        # Limitar número de tópicos
        top_topics = sorted_topics[:max_articles]
        
        for topic_insight in top_topics:
            topic = topic_insight.get("topic", "")
            facts = topic_insight.get("key_facts", [])
            
            if facts:
                article = self.generate_article(topic, facts)
                articles.append(article)
        
        logger.info(f"Geradas {len(articles)} matérias a partir dos tópicos em tendência")
        return articles
    
    def generate_all_articles(self, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Gera todas as matérias.
        
        Args:
            max_articles: Número máximo de artigos a gerar
            
        Returns:
            Lista de matérias geradas
        """
        # Carregar insights
        insights = self.load_insights()
        
        if not insights:
            logger.error("Não foi possível carregar os insights")
            return []
        
        # Extrair recomendações e insights de tópicos
        recommendations = insights.get("content_recommendations", [])
        topic_insights = insights.get("topic_insights", [])
        
        # Gerar matérias a partir das recomendações
        recommendation_articles = self.generate_articles_from_recommendations(recommendations)
        
        # Se não atingiu o número máximo, gerar mais matérias a partir dos tópicos em tendência
        remaining_articles = max_articles - len(recommendation_articles)
        
        if remaining_articles > 0:
            trending_articles = self.generate_articles_from_trending_topics(topic_insights, max_articles=remaining_articles)
            recommendation_articles.extend(trending_articles)
        
        # Limitar ao número máximo
        all_articles = recommendation_articles[:max_articles]
        
        # Salvar matérias
        output_path = "data/processed/materias.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Todas as matérias ({len(all_articles)}) salvas em {output_path}")
        return all_articles

if __name__ == "__main__":
    logger.info("Iniciando geração de matérias...")
    generator = ContentGenerator()
    articles = generator.generate_all_articles()
    
    if articles:
        logger.info("Geração de matérias concluída com sucesso")
    else:
        logger.error("Falha na geração de matérias")
