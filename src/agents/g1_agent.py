"""
Agente para coleta de dados do G1 (portal de notícias).
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any
import time
import random
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.utils.text_processor import TextProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class G1Agent(BaseAgent):
    """Agente para coleta de dados do portal G1."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o agente do G1.
        
        Args:
            config: Configurações do agente
        """
        super().__init__(config, "g1")
        self.base_url = config.get("base_url", "https://g1.globo.com")
        self.categories = config.get("categories", ["politica", "economia", "entretenimento"])
        self.max_articles = config.get("max_articles", 10)
        self.text_processor = TextProcessor()
        
        logger.info(f"Agente G1 inicializado com categorias: {self.categories}")
    
    def _get_category_url(self, category: str) -> str:
        """
        Obtém a URL da categoria.
        
        Args:
            category: Nome da categoria
            
        Returns:
            URL da categoria
        """
        category_mapping = {
            "politica": f"{self.base_url}/politica/",
            "economia": f"{self.base_url}/economia/",
            "entretenimento": f"{self.base_url}/pop-arte/",
            "tecnologia": f"{self.base_url}/tecnologia/",
            "esportes": f"{self.base_url}/esporte/",
            "educacao": f"{self.base_url}/educacao/",
            "saude": f"{self.base_url}/ciencia-e-saude/",
            "mundo": f"{self.base_url}/mundo/"
        }
        
        return category_mapping.get(category.lower(), f"{self.base_url}")
    
    def _extract_article_data(self, article_url: str) -> Dict[str, Any]:
        """
        Extrai dados de um artigo.
        
        Args:
            article_url: URL do artigo
            
        Returns:
            Dados do artigo
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(article_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair título
            title = ""
            title_tag = soup.find('h1', class_='content-head__title')
            if title_tag:
                title = title_tag.text.strip()
            
            # Extrair subtítulo
            subtitle = ""
            subtitle_tag = soup.find('h2', class_='content-head__subtitle')
            if subtitle_tag:
                subtitle = subtitle_tag.text.strip()
            
            # Extrair conteúdo
            content = ""
            content_div = soup.find('div', class_='content-text')
            if content_div:
                paragraphs = content_div.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs])
            
            # Extrair data de publicação
            published_date = ""
            date_tag = soup.find('time', class_='content-publication-data__updated')
            if date_tag:
                published_date = date_tag.text.strip()
            
            # Extrair autor
            author = ""
            author_tag = soup.find('p', class_='content-publication-data__from')
            if author_tag:
                author = author_tag.text.strip()
            
            # Extrair categoria/editoria
            category = ""
            breadcrumb = soup.find('div', class_='breadcrumb')
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if links and len(links) > 1:
                    category = links[1].text.strip()
            
            # Extrair imagem principal
            image_url = ""
            figure = soup.find('figure', class_='content-media__image')
            if figure:
                img = figure.find('img')
                if img and 'src' in img.attrs:
                    image_url = img['src']
            
            return {
                "title": title,
                "subtitle": subtitle,
                "content": content,
                "url": article_url,
                "published_date": published_date,
                "author": author,
                "category": category,
                "image_url": image_url,
                "source": "G1",
                "collected_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao extrair dados do artigo {article_url}: {e}")
            return {
                "title": "",
                "subtitle": "",
                "content": "",
                "url": article_url,
                "published_date": "",
                "author": "",
                "category": "",
                "image_url": "",
                "source": "G1",
                "collected_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Coleta dados do portal G1.
        
        Returns:
            Lista de artigos coletados
        """
        all_articles = []
        
        for category in self.categories:
            try:
                category_url = self._get_category_url(category)
                logger.info(f"Coletando artigos da categoria: {category} ({category_url})")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(category_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Encontrar links de artigos
                article_links = []
                feed_posts = soup.find_all('div', class_='feed-post')
                
                for post in feed_posts:
                    link = post.find('a')
                    if link and 'href' in link.attrs:
                        article_url = link['href']
                        if not article_url.startswith('http'):
                            article_url = f"https:{article_url}"
                        article_links.append(article_url)
                
                # Limitar o número de artigos por categoria
                max_per_category = min(len(article_links), self.max_articles // len(self.categories))
                article_links = article_links[:max_per_category]
                
                logger.info(f"Encontrados {len(article_links)} artigos na categoria {category}")
                
                # Extrair dados de cada artigo
                for url in article_links:
                    article_data = self._extract_article_data(url)
                    if article_data.get("title"):  # Verificar se o artigo foi extraído com sucesso
                        all_articles.append(article_data)
                    
                    # Pausa para evitar sobrecarga no servidor
                    time.sleep(random.uniform(1, 3))
            
            except Exception as e:
                logger.error(f"Erro ao coletar artigos da categoria {category}: {e}")
        
        logger.info(f"Total de {len(all_articles)} artigos coletados do G1")
        return all_articles
    
    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados coletados do G1.
        
        Args:
            data: Dados coletados
            
        Returns:
            Dados processados
        """
        processed_articles = []
        
        for article in data:
            try:
                # Verificar se o artigo tem conteúdo
                if not article.get("content"):
                    continue
                
                # Limpar o texto
                cleaned_content = self.text_processor.clean_text(article.get("content", ""))
                
                # Criar resumo
                summary = self.text_processor.summarize_text(cleaned_content)
                
                # Extrair entidades
                entities = self.text_processor.extract_entities(cleaned_content)
                
                # Calcular relevância (exemplo simples)
                relevance_keywords = ["política", "entretenimento", "notícias"]
                relevance_score = self.text_processor.calculate_relevance_score(
                    cleaned_content, relevance_keywords
                )
                
                # Criar artigo processado
                processed_article = {
                    "title": article.get("title", ""),
                    "subtitle": article.get("subtitle", ""),
                    "content": cleaned_content,
                    "summary": summary,
                    "url": article.get("url", ""),
                    "published_date": article.get("published_date", ""),
                    "author": article.get("author", ""),
                    "category": article.get("category", ""),
                    "image_url": article.get("image_url", ""),
                    "source": "G1",
                    "entities": entities,
                    "relevance_score": relevance_score,
                    "word_count": len(cleaned_content.split()),
                    "processed_at": datetime.now().isoformat()
                }
                
                processed_articles.append(processed_article)
            
            except Exception as e:
                logger.error(f"Erro ao processar artigo: {e}")
        
        # Ordenar por relevância
        processed_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        logger.info(f"Processados {len(processed_articles)} artigos do G1")
        return processed_articles
