"""
Agente para coleta de dados do Twitter usando a API.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.base_agent import BaseAgent
from src.utils.text_processor import TextProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterAgent(BaseAgent):
    """Agente para coleta de dados do Twitter."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o agente do Twitter.
        
        Args:
            config: Configurações do agente
        """
        super().__init__(config, "twitter")
        self.search_terms = config.get("search_terms", ["política", "entretenimento", "notícias"])
        self.max_tweets = config.get("max_tweets", 50)
        self.result_type = config.get("result_type", "popular")
        self.text_processor = TextProcessor()
        
        logger.info(f"Agente Twitter inicializado com termos de busca: {self.search_terms}")
    
    def _search_twitter(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Realiza uma busca no Twitter usando a API.
        
        Args:
            query: Termo de busca
            count: Número máximo de tweets a retornar
            
        Returns:
            Lista de tweets encontrados
        """
        try:
            import sys
            sys.path.append('/opt/.manus/.sandbox-runtime')
            from data_api import ApiClient
            client = ApiClient()
            
            # Usar a API de busca do Twitter
            search_results = client.call_api('Twitter/search_twitter', query={
                'query': query,
                'count': count,
                'type': self.result_type.capitalize()
            })
            
            # Processar os resultados
            tweets = []
            
            if not search_results or 'result' not in search_results:
                logger.warning(f"Nenhum resultado encontrado para a busca: {query}")
                return []
            
            # Extrair tweets dos resultados
            timeline = search_results.get('result', {}).get('timeline', {})
            instructions = timeline.get('instructions', [])
            
            for instruction in instructions:
                entries = instruction.get('entries', [])
                
                for entry in entries:
                    content = entry.get('content', {})
                    
                    # Verificar se é um tweet
                    if content.get('__typename') == 'TimelineTimelineItem':
                        items = content.get('items', [])
                        
                        for item in items:
                            item_content = item.get('item', {}).get('itemContent', {})
                            
                            # Extrair dados do tweet
                            if item_content.get('__typename') == 'TimelineTweet':
                                tweet_results = item_content.get('tweet_results', {})
                                result = tweet_results.get('result', {})
                                
                                # Extrair informações do usuário
                                user_results = result.get('core', {}).get('user_results', {})
                                user_result = user_results.get('result', {})
                                user_legacy = user_result.get('legacy', {})
                                
                                # Extrair conteúdo do tweet
                                legacy = result.get('legacy', {})
                                
                                tweet = {
                                    'id': result.get('rest_id', ''),
                                    'text': legacy.get('full_text', ''),
                                    'created_at': legacy.get('created_at', ''),
                                    'retweet_count': legacy.get('retweet_count', 0),
                                    'favorite_count': legacy.get('favorite_count', 0),
                                    'reply_count': legacy.get('reply_count', 0),
                                    'quote_count': legacy.get('quote_count', 0),
                                    'user': {
                                        'id': user_result.get('rest_id', ''),
                                        'name': user_legacy.get('name', ''),
                                        'screen_name': user_legacy.get('screen_name', ''),
                                        'followers_count': user_legacy.get('followers_count', 0),
                                        'verified': user_legacy.get('verified', False),
                                        'profile_image_url': user_legacy.get('profile_image_url_https', '')
                                    },
                                    'source': 'Twitter',
                                    'collected_at': datetime.now().isoformat()
                                }
                                
                                tweets.append(tweet)
            
            logger.info(f"Encontrados {len(tweets)} tweets para a busca: {query}")
            return tweets
        
        except Exception as e:
            logger.error(f"Erro ao buscar tweets para {query}: {e}")
            return []
    
    def _get_user_tweets(self, username: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Obtém tweets de um usuário específico.
        
        Args:
            username: Nome de usuário
            count: Número máximo de tweets a retornar
            
        Returns:
            Lista de tweets do usuário
        """
        try:
            import sys
            sys.path.append('/opt/.manus/.sandbox-runtime')
            from data_api import ApiClient
            client = ApiClient()
            
            # Primeiro, obter o ID do usuário
            user_profile = client.call_api('Twitter/get_user_profile_by_username', query={
                'username': username
            })
            
            if not user_profile or 'result' not in user_profile:
                logger.warning(f"Perfil não encontrado para o usuário: {username}")
                return []
            
            # Extrair o ID do usuário
            user_data = user_profile.get('result', {}).get('data', {}).get('user', {}).get('result', {})
            user_id = user_data.get('rest_id', '')
            
            if not user_id:
                logger.warning(f"ID não encontrado para o usuário: {username}")
                return []
            
            # Obter tweets do usuário
            user_tweets = client.call_api('Twitter/get_user_tweets', query={
                'user': user_id,
                'count': count
            })
            
            # Processar os resultados
            tweets = []
            
            if not user_tweets or 'result' not in user_tweets:
                logger.warning(f"Nenhum tweet encontrado para o usuário: {username}")
                return []
            
            # Extrair tweets dos resultados
            timeline = user_tweets.get('result', {}).get('timeline', {})
            instructions = timeline.get('instructions', [])
            
            for instruction in instructions:
                entries = instruction.get('entries', [])
                
                for entry in entries:
                    content = entry.get('content', {})
                    
                    # Verificar se é um tweet
                    if content.get('entryType') == 'TimelineTimelineItem':
                        item_content = content.get('itemContent', {})
                        
                        # Extrair dados do tweet
                        if item_content.get('itemType') == 'TimelineTweet':
                            tweet_results = item_content.get('tweet_results', {})
                            result = tweet_results.get('result', {})
                            
                            # Extrair conteúdo do tweet
                            legacy = result.get('legacy', {})
                            
                            tweet = {
                                'id': result.get('rest_id', ''),
                                'text': legacy.get('full_text', ''),
                                'created_at': legacy.get('created_at', ''),
                                'retweet_count': legacy.get('retweet_count', 0),
                                'favorite_count': legacy.get('favorite_count', 0),
                                'reply_count': legacy.get('reply_count', 0),
                                'quote_count': legacy.get('quote_count', 0),
                                'user': {
                                    'id': user_id,
                                    'name': user_data.get('legacy', {}).get('name', ''),
                                    'screen_name': username,
                                    'followers_count': user_data.get('legacy', {}).get('followers_count', 0),
                                    'verified': user_data.get('legacy', {}).get('verified', False),
                                    'profile_image_url': user_data.get('legacy', {}).get('profile_image_url_https', '')
                                },
                                'source': 'Twitter',
                                'collected_at': datetime.now().isoformat()
                            }
                            
                            tweets.append(tweet)
            
            logger.info(f"Encontrados {len(tweets)} tweets do usuário: {username}")
            return tweets
        
        except Exception as e:
            logger.error(f"Erro ao obter tweets do usuário {username}: {e}")
            return []
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Coleta dados do Twitter.
        
        Returns:
            Lista de tweets coletados
        """
        all_tweets = []
        
        # Coletar tweets por termos de busca
        for term in self.search_terms:
            try:
                logger.info(f"Buscando tweets para o termo: {term}")
                tweets = self._search_twitter(term, count=min(self.max_tweets // len(self.search_terms), 100))
                all_tweets.extend(tweets)
            except Exception as e:
                logger.error(f"Erro ao buscar tweets para o termo {term}: {e}")
        
        # Coletar tweets de perfis de notícias relevantes
        news_accounts = ["g1", "bbcbrasil", "cnnbrasil", "folha", "estadao"]
        for account in news_accounts:
            try:
                logger.info(f"Coletando tweets do perfil: {account}")
                tweets = self._get_user_tweets(account, count=10)
                all_tweets.extend(tweets)
            except Exception as e:
                logger.error(f"Erro ao coletar tweets do perfil {account}: {e}")
        
        # Remover duplicatas (pelo ID do tweet)
        unique_tweets = {tweet['id']: tweet for tweet in all_tweets if 'id' in tweet}
        all_tweets = list(unique_tweets.values())
        
        logger.info(f"Total de {len(all_tweets)} tweets coletados")
        return all_tweets
    
    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados coletados do Twitter.
        
        Args:
            data: Dados coletados
            
        Returns:
            Dados processados
        """
        processed_tweets = []
        
        for tweet in data:
            try:
                # Verificar se o tweet tem conteúdo
                if not tweet.get("text"):
                    continue
                
                # Limpar o texto
                cleaned_text = self.text_processor.clean_text(tweet.get("text", ""))
                
                # Calcular engajamento
                engagement_score = (
                    tweet.get("retweet_count", 0) * 2 + 
                    tweet.get("favorite_count", 0) + 
                    tweet.get("reply_count", 0) * 1.5 + 
                    tweet.get("quote_count", 0) * 1.5
                )
                
                # Normalizar engajamento com base nos seguidores (se disponível)
                followers = tweet.get("user", {}).get("followers_count", 0)
                if followers > 0:
                    normalized_engagement = engagement_score / (followers ** 0.5)
                else:
                    normalized_engagement = 0
                
                # Calcular relevância
                relevance_keywords = ["política", "entretenimento", "notícias"]
                relevance_score = self.text_processor.calculate_relevance_score(
                    cleaned_text, relevance_keywords
                )
                
                # Extrair entidades
                entities = self.text_processor.extract_entities(cleaned_text)
                
                # Criar tweet processado
                processed_tweet = {
                    "id": tweet.get("id", ""),
                    "text": cleaned_text,
                    "created_at": tweet.get("created_at", ""),
                    "user": tweet.get("user", {}),
                    "engagement": {
                        "retweet_count": tweet.get("retweet_count", 0),
                        "favorite_count": tweet.get("favorite_count", 0),
                        "reply_count": tweet.get("reply_count", 0),
                        "quote_count": tweet.get("quote_count", 0),
                        "total_engagement": engagement_score,
                        "normalized_engagement": normalized_engagement
                    },
                    "source": "Twitter",
                    "entities": entities,
                    "relevance_score": relevance_score,
                    "word_count": len(cleaned_text.split()),
                    "processed_at": datetime.now().isoformat()
                }
                
                processed_tweets.append(processed_tweet)
            
            except Exception as e:
                logger.error(f"Erro ao processar tweet: {e}")
        
        # Ordenar por engajamento normalizado e relevância
        processed_tweets.sort(
            key=lambda x: (
                x.get("engagement", {}).get("normalized_engagement", 0) * 0.7 + 
                x.get("relevance_score", 0) * 0.3
            ), 
            reverse=True
        )
        
        logger.info(f"Processados {len(processed_tweets)} tweets")
        return processed_tweets
