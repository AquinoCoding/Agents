"""
Agente para coleta de dados do Instagram usando Instaloader.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import time
import random
import instaloader
import os
import tempfile
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.utils.text_processor import TextProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramAgent(BaseAgent):
    """Agente para coleta de dados do Instagram."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o agente do Instagram.
        
        Args:
            config: Configurações do agente
        """
        super().__init__(config, "instagram")
        self.profiles = config.get("profiles", ["g1", "bbcbrasil", "cnnbrasil"])
        self.hashtags = config.get("hashtags", ["noticia", "politica", "entretenimento"])
        self.max_posts = config.get("max_posts", 20)
        self.text_processor = TextProcessor()
        
        # Inicializar o Instaloader
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Criar diretório temporário para downloads
        self.temp_dir = tempfile.mkdtemp()
        
        logger.info(f"Agente Instagram inicializado com perfis: {self.profiles} e hashtags: {self.hashtags}")
    
    def _get_profile_posts(self, profile_name: str, max_count: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém posts de um perfil do Instagram.
        
        Args:
            profile_name: Nome do perfil
            max_count: Número máximo de posts a retornar
            
        Returns:
            Lista de posts do perfil
        """
        posts = []
        
        try:
            # Obter perfil
            profile = instaloader.Profile.from_username(self.loader.context, profile_name)
            
            # Obter posts
            count = 0
            for post in profile.get_posts():
                if count >= max_count:
                    break
                
                # Extrair dados do post
                post_data = {
                    "id": post.shortcode,
                    "caption": post.caption if post.caption else "",
                    "date": post.date_local.isoformat(),
                    "likes": post.likes,
                    "comments": post.comments,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "is_video": post.is_video,
                    "location": post.location.name if post.location else "",
                    "hashtags": list(post.caption_hashtags) if post.caption else [],
                    "mentions": list(post.caption_mentions) if post.caption else [],
                    "profile": {
                        "username": profile.username,
                        "full_name": profile.full_name,
                        "followers": profile.followers,
                        "biography": profile.biography,
                        "is_verified": profile.is_verified
                    },
                    "source": "Instagram",
                    "collected_at": datetime.now().isoformat()
                }
                
                posts.append(post_data)
                count += 1
                
                # Pausa para evitar limitação de taxa
                time.sleep(random.uniform(1, 2))
            
            logger.info(f"Coletados {len(posts)} posts do perfil {profile_name}")
            return posts
        
        except Exception as e:
            logger.error(f"Erro ao coletar posts do perfil {profile_name}: {e}")
            return []
    
    def _get_hashtag_posts(self, hashtag: str, max_count: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém posts de uma hashtag do Instagram.
        
        Args:
            hashtag: Nome da hashtag (sem #)
            max_count: Número máximo de posts a retornar
            
        Returns:
            Lista de posts da hashtag
        """
        posts = []
        
        try:
            # Obter posts da hashtag
            count = 0
            for post in self.loader.get_hashtag_posts(hashtag):
                if count >= max_count:
                    break
                
                # Extrair dados do post
                post_data = {
                    "id": post.shortcode,
                    "caption": post.caption if post.caption else "",
                    "date": post.date_local.isoformat(),
                    "likes": post.likes,
                    "comments": post.comments,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "is_video": post.is_video,
                    "location": post.location.name if post.location else "",
                    "hashtags": list(post.caption_hashtags) if post.caption else [],
                    "mentions": list(post.caption_mentions) if post.caption else [],
                    "profile": {
                        "username": post.owner_username,
                        "profile_id": post.owner_id
                    },
                    "source": "Instagram",
                    "collected_at": datetime.now().isoformat()
                }
                
                posts.append(post_data)
                count += 1
                
                # Pausa para evitar limitação de taxa
                time.sleep(random.uniform(1, 2))
            
            logger.info(f"Coletados {len(posts)} posts da hashtag #{hashtag}")
            return posts
        
        except Exception as e:
            logger.error(f"Erro ao coletar posts da hashtag #{hashtag}: {e}")
            return []
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Coleta dados do Instagram.
        
        Returns:
            Lista de posts coletados
        """
        all_posts = []
        
        # Coletar posts de perfis
        for profile in self.profiles:
            try:
                logger.info(f"Coletando posts do perfil: {profile}")
                posts = self._get_profile_posts(profile, max_count=min(self.max_posts // len(self.profiles), 10))
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Erro ao coletar posts do perfil {profile}: {e}")
        
        # Coletar posts de hashtags
        for hashtag in self.hashtags:
            try:
                logger.info(f"Coletando posts da hashtag: #{hashtag}")
                posts = self._get_hashtag_posts(hashtag, max_count=min(self.max_posts // len(self.hashtags), 10))
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Erro ao coletar posts da hashtag #{hashtag}: {e}")
        
        # Remover duplicatas (pelo ID do post)
        unique_posts = {post['id']: post for post in all_posts if 'id' in post}
        all_posts = list(unique_posts.values())
        
        logger.info(f"Total de {len(all_posts)} posts coletados do Instagram")
        return all_posts
    
    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados coletados do Instagram.
        
        Args:
            data: Dados coletados
            
        Returns:
            Dados processados
        """
        processed_posts = []
        
        for post in data:
            try:
                # Verificar se o post tem conteúdo
                if not post.get("caption"):
                    continue
                
                # Limpar o texto
                cleaned_caption = self.text_processor.clean_text(post.get("caption", ""))
                
                # Calcular engajamento
                engagement_score = post.get("likes", 0) + post.get("comments", 0) * 2
                
                # Normalizar engajamento com base nos seguidores (se disponível)
                followers = post.get("profile", {}).get("followers", 0)
                if followers > 0:
                    normalized_engagement = engagement_score / (followers ** 0.5)
                else:
                    normalized_engagement = 0
                
                # Calcular relevância
                relevance_keywords = ["política", "entretenimento", "notícias"]
                relevance_score = self.text_processor.calculate_relevance_score(
                    cleaned_caption, relevance_keywords
                )
                
                # Extrair entidades
                entities = self.text_processor.extract_entities(cleaned_caption)
                
                # Criar post processado
                processed_post = {
                    "id": post.get("id", ""),
                    "caption": cleaned_caption,
                    "date": post.get("date", ""),
                    "url": post.get("url", ""),
                    "profile": post.get("profile", {}),
                    "engagement": {
                        "likes": post.get("likes", 0),
                        "comments": post.get("comments", 0),
                        "total_engagement": engagement_score,
                        "normalized_engagement": normalized_engagement
                    },
                    "hashtags": post.get("hashtags", []),
                    "mentions": post.get("mentions", []),
                    "source": "Instagram",
                    "entities": entities,
                    "relevance_score": relevance_score,
                    "word_count": len(cleaned_caption.split()),
                    "processed_at": datetime.now().isoformat()
                }
                
                processed_posts.append(processed_post)
            
            except Exception as e:
                logger.error(f"Erro ao processar post: {e}")
        
        # Ordenar por engajamento normalizado e relevância
        processed_posts.sort(
            key=lambda x: (
                x.get("engagement", {}).get("normalized_engagement", 0) * 0.7 + 
                x.get("relevance_score", 0) * 0.3
            ), 
            reverse=True
        )
        
        logger.info(f"Processados {len(processed_posts)} posts do Instagram")
        return processed_posts
    
    def __del__(self):
        """Limpar recursos ao destruir o objeto."""
        # Remover diretório temporário
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
