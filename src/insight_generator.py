"""
Gerador de insights e métricas a partir dos dados processados.
"""

import logging
import json
from typing import List, Dict, Any
import os
from pathlib import Path
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config.config import METRICS_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InsightGenerator:
    """Gerador de insights e métricas a partir dos dados processados."""
    
    def __init__(self):
        """Inicializa o gerador de insights."""
        self.engagement_threshold = METRICS_CONFIG.get("engagement_threshold", 0.5)
        self.trending_threshold = METRICS_CONFIG.get("trending_threshold", 0.7)
        self.sentiment_analysis = METRICS_CONFIG.get("sentiment_analysis", True)
        
        # Criar diretórios para saída
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("data/processed/insights", exist_ok=True)
        os.makedirs("data/processed/visualizations", exist_ok=True)
        
        logger.info("Gerador de insights inicializado")
    
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
    
    def generate_source_distribution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera distribuição de fontes.
        
        Args:
            data: Dados consolidados
            
        Returns:
            Distribuição de fontes
        """
        # Extrair todos os itens
        all_items = []
        for topic_items in data.get("topics", {}).values():
            all_items.extend(topic_items)
        
        # Contar itens por fonte
        source_counts = {}
        for item in all_items:
            source = item.get("source", "Desconhecido")
            if source not in source_counts:
                source_counts[source] = 0
            source_counts[source] += 1
        
        # Calcular percentuais
        total_items = len(all_items)
        source_distribution = {
            source: {
                "count": count,
                "percentage": (count / total_items) * 100 if total_items > 0 else 0
            }
            for source, count in source_counts.items()
        }
        
        # Criar visualização
        if source_counts:
            plt.figure(figsize=(10, 6))
            sns.barplot(x=list(source_counts.keys()), y=list(source_counts.values()))
            plt.title("Distribuição de Conteúdo por Fonte")
            plt.xlabel("Fonte")
            plt.ylabel("Quantidade de Itens")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("data/processed/visualizations/source_distribution.png")
            plt.close()
        
        logger.info(f"Distribuição de fontes gerada: {len(source_distribution)} fontes")
        return source_distribution
    
    def generate_topic_insights(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera insights sobre os tópicos.
        
        Args:
            data: Dados consolidados
            
        Returns:
            Lista de insights sobre tópicos
        """
        trending_topics = data.get("trending_topics", [])
        
        topic_insights = []
        for topic in trending_topics:
            topic_name = topic.get("topic", "")
            count = topic.get("count", 0)
            avg_engagement = topic.get("avg_engagement", 0)
            sources = topic.get("sources", [])
            key_facts = topic.get("key_facts", [])
            
            # Calcular pontuação de tendência
            trend_score = (count * 0.6) + (avg_engagement * 0.4)
            
            # Determinar status de tendência
            if trend_score > self.trending_threshold:
                trend_status = "Alta"
            elif trend_score > self.trending_threshold / 2:
                trend_status = "Média"
            else:
                trend_status = "Baixa"
            
            # Criar insight
            insight = {
                "topic": topic_name,
                "mentions": count,
                "engagement": avg_engagement,
                "trend_score": trend_score,
                "trend_status": trend_status,
                "sources": sources,
                "key_facts": key_facts,
                "summary": f"O tópico '{topic_name}' apresenta tendência {trend_status.lower()} com {count} menções e engajamento médio de {avg_engagement:.2f}."
            }
            
            topic_insights.append(insight)
        
        # Ordenar por pontuação de tendência
        topic_insights.sort(key=lambda x: x.get("trend_score", 0), reverse=True)
        
        # Criar visualização de tópicos em tendência
        if topic_insights:
            topics = [insight["topic"] for insight in topic_insights[:10]]
            scores = [insight["trend_score"] for insight in topic_insights[:10]]
            
            plt.figure(figsize=(12, 6))
            bars = plt.barh(topics, scores, color=plt.cm.viridis(np.linspace(0, 1, len(topics))))
            plt.title("Tópicos em Tendência")
            plt.xlabel("Pontuação de Tendência")
            plt.tight_layout()
            plt.savefig("data/processed/visualizations/trending_topics.png")
            plt.close()
        
        logger.info(f"Insights de tópicos gerados: {len(topic_insights)} tópicos")
        return topic_insights
    
    def generate_engagement_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera métricas de engajamento.
        
        Args:
            data: Dados consolidados
            
        Returns:
            Métricas de engajamento
        """
        # Extrair todos os itens
        all_items = []
        for topic_items in data.get("topics", {}).values():
            all_items.extend(topic_items)
        
        # Extrair métricas de engajamento por fonte
        engagement_by_source = {}
        
        for item in all_items:
            source = item.get("source", "Desconhecido")
            
            if source not in engagement_by_source:
                engagement_by_source[source] = {
                    "total_items": 0,
                    "total_engagement": 0,
                    "avg_engagement": 0,
                    "high_engagement_items": 0
                }
            
            engagement_by_source[source]["total_items"] += 1
            
            # Extrair engajamento
            engagement = item.get("engagement", {})
            engagement_value = 0
            
            if isinstance(engagement, dict):
                if "normalized_engagement" in engagement:
                    engagement_value = engagement["normalized_engagement"]
                elif "total_engagement" in engagement:
                    engagement_value = engagement["total_engagement"]
            
            engagement_by_source[source]["total_engagement"] += engagement_value
            
            # Contar itens de alto engajamento
            if engagement_value > self.engagement_threshold:
                engagement_by_source[source]["high_engagement_items"] += 1
        
        # Calcular médias
        for source, metrics in engagement_by_source.items():
            if metrics["total_items"] > 0:
                metrics["avg_engagement"] = metrics["total_engagement"] / metrics["total_items"]
                metrics["high_engagement_percentage"] = (metrics["high_engagement_items"] / metrics["total_items"]) * 100
            else:
                metrics["avg_engagement"] = 0
                metrics["high_engagement_percentage"] = 0
        
        # Criar visualização de engajamento por fonte
        if engagement_by_source:
            sources = list(engagement_by_source.keys())
            avg_engagements = [metrics["avg_engagement"] for metrics in engagement_by_source.values()]
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(sources, avg_engagements, color=plt.cm.cool(np.linspace(0, 1, len(sources))))
            plt.title("Engajamento Médio por Fonte")
            plt.xlabel("Fonte")
            plt.ylabel("Engajamento Médio")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("data/processed/visualizations/engagement_by_source.png")
            plt.close()
        
        logger.info(f"Métricas de engajamento geradas para {len(engagement_by_source)} fontes")
        return engagement_by_source
    
    def generate_content_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera recomendações de conteúdo.
        
        Args:
            data: Dados consolidados
            
        Returns:
            Lista de recomendações de conteúdo
        """
        trending_topics = data.get("trending_topics", [])
        
        # Filtrar tópicos com alta tendência
        high_trend_topics = [
            topic for topic in trending_topics 
            if (topic.get("count", 0) * 0.6 + topic.get("avg_engagement", 0) * 0.4) > self.trending_threshold
        ]
        
        recommendations = []
        for topic in high_trend_topics:
            topic_name = topic.get("topic", "")
            key_facts = topic.get("key_facts", [])
            
            # Criar recomendação
            recommendation = {
                "topic": topic_name,
                "key_facts": key_facts,
                "recommendation": f"Criar matéria sobre '{topic_name}' com base nos fatos coletados.",
                "priority": "Alta" if len(key_facts) >= 3 else "Média"
            }
            
            recommendations.append(recommendation)
        
        # Adicionar recomendações para tópicos com tendência média
        medium_trend_topics = [
            topic for topic in trending_topics 
            if (topic.get("count", 0) * 0.6 + topic.get("avg_engagement", 0) * 0.4) > self.trending_threshold / 2
            and (topic.get("count", 0) * 0.6 + topic.get("avg_engagement", 0) * 0.4) <= self.trending_threshold
        ]
        
        for topic in medium_trend_topics:
            topic_name = topic.get("topic", "")
            key_facts = topic.get("key_facts", [])
            
            if len(key_facts) >= 2:
                recommendation = {
                    "topic": topic_name,
                    "key_facts": key_facts,
                    "recommendation": f"Considerar matéria sobre '{topic_name}' se houver desenvolvimento adicional.",
                    "priority": "Média"
                }
                
                recommendations.append(recommendation)
        
        logger.info(f"Recomendações de conteúdo geradas: {len(recommendations)} recomendações")
        return recommendations
    
    def generate_all_insights(self) -> Dict[str, Any]:
        """
        Gera todos os insights e métricas.
        
        Returns:
            Todos os insights e métricas
        """
        # Carregar dados consolidados
        data = self.load_consolidated_data()
        
        if not data:
            logger.error("Não foi possível carregar os dados consolidados")
            return {}
        
        # Gerar insights e métricas
        source_distribution = self.generate_source_distribution(data)
        topic_insights = self.generate_topic_insights(data)
        engagement_metrics = self.generate_engagement_metrics(data)
        content_recommendations = self.generate_content_recommendations(data)
        
        # Consolidar insights
        all_insights = {
            "source_distribution": source_distribution,
            "topic_insights": topic_insights,
            "engagement_metrics": engagement_metrics,
            "content_recommendations": content_recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        # Salvar insights
        output_path = "data/processed/insights.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_insights, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Todos os insights e métricas salvos em {output_path}")
        return all_insights

if __name__ == "__main__":
    logger.info("Iniciando geração de insights...")
    generator = InsightGenerator()
    insights = generator.generate_all_insights()
    
    if insights:
        logger.info("Geração de insights concluída com sucesso")
    else:
        logger.error("Falha na geração de insights")
