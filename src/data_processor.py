"""
Processador de dados coletados pelos agentes.
Responsável por analisar, filtrar e consolidar os dados para geração de insights e matérias.
"""

import logging
import json
from typing import List, Dict, Any, Tuple
import os
from pathlib import Path
import sys
from datetime import datetime
import pandas as pd
import nltk
from collections import Counter

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.text_processor import TextProcessor
from src.config.config import PROCESSING_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    """Processador de dados coletados pelos agentes."""
    
    def __init__(self):
        """Inicializa o processador de dados."""
        self.text_processor = TextProcessor()
        self.min_relevance_score = PROCESSING_CONFIG.get("min_relevance_score", 0.6)
        self.max_content_length = PROCESSING_CONFIG.get("max_content_length", 1000)
        self.language = PROCESSING_CONFIG.get("language", "pt-br")
        
        # Criar diretório para dados processados
        os.makedirs("data/processed", exist_ok=True)
        
        logger.info("Processador de dados inicializado")
    
    def load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Carrega dados de um arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dados carregados
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Dados carregados de {file_path}: {len(data)} itens")
            return data
        except Exception as e:
            logger.error(f"Erro ao carregar dados de {file_path}: {e}")
            return []
    
    def filter_by_relevance(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra os dados por relevância.
        
        Args:
            data: Dados a serem filtrados
            
        Returns:
            Dados filtrados
        """
        filtered_data = [
            item for item in data 
            if item.get("relevance_score", 0) >= self.min_relevance_score
        ]
        
        logger.info(f"Filtrados {len(filtered_data)} itens por relevância (de {len(data)})")
        return filtered_data
    
    def filter_by_engagement(self, data: List[Dict[str, Any]], min_percentile: float = 0.3) -> List[Dict[str, Any]]:
        """
        Filtra os dados por engajamento.
        
        Args:
            data: Dados a serem filtrados
            min_percentile: Percentil mínimo de engajamento
            
        Returns:
            Dados filtrados
        """
        if not data:
            return []
        
        # Extrair valores de engajamento
        engagement_values = []
        for item in data:
            engagement = item.get("engagement", {})
            if isinstance(engagement, dict) and "normalized_engagement" in engagement:
                engagement_values.append(engagement["normalized_engagement"])
            elif isinstance(engagement, dict) and "total_engagement" in engagement:
                engagement_values.append(engagement["total_engagement"])
            else:
                engagement_values.append(0)
        
        # Calcular limiar de engajamento
        if engagement_values:
            threshold = pd.Series(engagement_values).quantile(min_percentile)
        else:
            threshold = 0
        
        # Filtrar por engajamento
        filtered_data = []
        for i, item in enumerate(data):
            if engagement_values[i] >= threshold:
                filtered_data.append(item)
        
        logger.info(f"Filtrados {len(filtered_data)} itens por engajamento (de {len(data)})")
        return filtered_data
    
    def group_by_topic(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa os dados por tópico.
        
        Args:
            data: Dados a serem agrupados
            
        Returns:
            Dados agrupados por tópico
        """
        # Extrair entidades e palavras-chave de todos os itens
        all_entities = []
        for item in data:
            entities = item.get("entities", [])
            if entities:
                all_entities.extend(entities)
        
        # Contar frequência das entidades
        entity_counter = Counter(all_entities)
        top_entities = [entity for entity, count in entity_counter.most_common(10) if count > 1]
        
        # Agrupar por tópico (usando entidades como tópicos)
        topics = {}
        for entity in top_entities:
            topics[entity] = []
            for item in data:
                item_entities = item.get("entities", [])
                if entity in item_entities:
                    topics[entity].append(item)
        
        # Adicionar grupo "outros" para itens não classificados
        classified_items = set()
        for topic_items in topics.values():
            for item in topic_items:
                classified_items.add(id(item))
        
        topics["outros"] = [item for item in data if id(item) not in classified_items]
        
        logger.info(f"Dados agrupados em {len(topics)} tópicos")
        return topics
    
    def extract_trending_topics(self, data: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Extrai tópicos em tendência dos dados.
        
        Args:
            data: Dados para extração de tendências
            top_n: Número de tópicos a retornar
            
        Returns:
            Lista de tópicos em tendência
        """
        # Extrair todas as entidades e hashtags
        all_entities = []
        all_hashtags = []
        
        for item in data:
            # Entidades
            entities = item.get("entities", [])
            if entities:
                all_entities.extend(entities)
            
            # Hashtags (para dados do Twitter e Instagram)
            hashtags = item.get("hashtags", [])
            if hashtags:
                all_hashtags.extend(hashtags)
        
        # Contar frequência
        entity_counter = Counter(all_entities)
        hashtag_counter = Counter(all_hashtags)
        
        # Combinar entidades e hashtags
        combined_counter = entity_counter + hashtag_counter
        
        # Extrair tópicos em tendência
        trending_topics = []
        for topic, count in combined_counter.most_common(top_n):
            # Encontrar itens relacionados a este tópico
            related_items = []
            for item in data:
                entities = item.get("entities", [])
                hashtags = item.get("hashtags", [])
                
                if topic in entities or topic in hashtags:
                    related_items.append(item)
            
            # Calcular engajamento médio
            avg_engagement = 0
            if related_items:
                engagement_sum = 0
                for item in related_items:
                    engagement = item.get("engagement", {})
                    if isinstance(engagement, dict):
                        if "normalized_engagement" in engagement:
                            engagement_sum += engagement["normalized_engagement"]
                        elif "total_engagement" in engagement:
                            engagement_sum += engagement["total_engagement"]
                
                avg_engagement = engagement_sum / len(related_items)
            
            trending_topics.append({
                "topic": topic,
                "count": count,
                "avg_engagement": avg_engagement,
                "sources": list(set(item.get("source", "") for item in related_items)),
                "related_items_count": len(related_items)
            })
        
        logger.info(f"Extraídos {len(trending_topics)} tópicos em tendência")
        return trending_topics
    
    def extract_key_facts(self, data: List[Dict[str, Any]], topic: str) -> List[str]:
        """
        Extrai fatos-chave sobre um tópico.
        
        Args:
            data: Dados para extração de fatos
            topic: Tópico para extração de fatos
            
        Returns:
            Lista de fatos-chave
        """
        # Filtrar itens relacionados ao tópico
        related_items = []
        for item in data:
            entities = item.get("entities", [])
            hashtags = item.get("hashtags", [])
            
            content = ""
            if "content" in item:
                content = item["content"]
            elif "text" in item:
                content = item["text"]
            elif "caption" in item:
                content = item["caption"]
            
            if topic in entities or topic in hashtags or topic.lower() in content.lower():
                related_items.append(item)
        
        # Extrair sentenças relevantes
        sentences = []
        for item in related_items:
            content = ""
            if "content" in item:
                content = item["content"]
            elif "text" in item:
                content = item["text"]
            elif "caption" in item:
                content = item["caption"]
            
            if content:
                item_sentences = nltk.sent_tokenize(content)
                for sentence in item_sentences:
                    if topic.lower() in sentence.lower():
                        sentences.append(sentence)
        
        # Remover duplicatas e sentenças muito curtas
        unique_sentences = list(set(sentences))
        filtered_sentences = [s for s in unique_sentences if len(s.split()) > 5]
        
        # Limitar número de fatos
        max_facts = min(len(filtered_sentences), 10)
        key_facts = filtered_sentences[:max_facts]
        
        logger.info(f"Extraídos {len(key_facts)} fatos-chave sobre o tópico '{topic}'")
        return key_facts
    
    def consolidate_data(self, data_files: List[str]) -> Dict[str, Any]:
        """
        Consolida dados de múltiplos arquivos.
        
        Args:
            data_files: Lista de caminhos de arquivos
            
        Returns:
            Dados consolidados
        """
        all_data = []
        
        for file_path in data_files:
            data = self.load_data(file_path)
            all_data.extend(data)
        
        # Filtrar por relevância
        filtered_data = self.filter_by_relevance(all_data)
        
        # Filtrar por engajamento
        filtered_data = self.filter_by_engagement(filtered_data)
        
        # Agrupar por tópico
        grouped_data = self.group_by_topic(filtered_data)
        
        # Extrair tópicos em tendência
        trending_topics = self.extract_trending_topics(filtered_data)
        
        # Extrair fatos-chave para cada tópico em tendência
        for topic in trending_topics:
            topic_name = topic["topic"]
            key_facts = self.extract_key_facts(filtered_data, topic_name)
            topic["key_facts"] = key_facts
        
        # Consolidar resultados
        consolidated_data = {
            "total_items": len(all_data),
            "filtered_items": len(filtered_data),
            "topics": grouped_data,
            "trending_topics": trending_topics,
            "processed_at": datetime.now().isoformat()
        }
        
        # Salvar dados consolidados
        output_path = "data/processed/consolidated_data.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dados consolidados salvos em {output_path}")
        return consolidated_data
    
    def process_all_data(self) -> Dict[str, Any]:
        """
        Processa todos os dados coletados.
        
        Returns:
            Dados processados
        """
        # Encontrar arquivos de dados processados
        data_dir = Path("data/raw")
        data_files = []
        
        for source_dir in data_dir.iterdir():
            if source_dir.is_dir():
                for file in source_dir.glob("*_processed.json"):
                    data_files.append(str(file))
        
        if not data_files:
            logger.warning("Nenhum arquivo de dados processados encontrado")
            return {}
        
        logger.info(f"Encontrados {len(data_files)} arquivos de dados processados")
        return self.consolidate_data(data_files)

if __name__ == "__main__":
    logger.info("Iniciando processamento de dados...")
    processor = DataProcessor()
    processed_data = processor.process_all_data()
    
    if processed_data:
        logger.info("Processamento de dados concluído com sucesso")
    else:
        logger.error("Falha no processamento de dados")
