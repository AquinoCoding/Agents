"""
Utilitários para processamento de texto e análise de relevância.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from typing import List, Dict, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextProcessor:
    """Classe para processamento e análise de texto."""
    
    def __init__(self):
        """Inicializa o processador de texto."""
        # Baixar recursos do NLTK necessários
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('rslp', quiet=True)
            self.stop_words = set(stopwords.words('portuguese'))
            self.stemmer = RSLPStemmer()
        except Exception as e:
            logger.error(f"Erro ao inicializar recursos NLTK: {e}")
            self.stop_words = set()
            self.stemmer = None
    
    def clean_text(self, text: str) -> str:
        """
        Limpa o texto removendo caracteres especiais e formatação.
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo
        """
        if not text:
            return ""
            
        # Remover URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remover tags HTML
        text = re.sub(r'<.*?>', '', text)
        
        # Remover caracteres especiais e números
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza o texto em palavras.
        
        Args:
            text: Texto a ser tokenizado
            
        Returns:
            Lista de tokens
        """
        if not text:
            return []
            
        return word_tokenize(text.lower())
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords dos tokens.
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Lista de tokens sem stopwords
        """
        if not tokens:
            return []
            
        return [token for token in tokens if token not in self.stop_words]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Aplica stemming nos tokens.
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Lista de tokens com stemming
        """
        if not tokens or not self.stemmer:
            return tokens
            
        return [self.stemmer.stem(token) for token in tokens]
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Pré-processa o texto completo (limpeza, tokenização, remoção de stopwords, stemming).
        
        Args:
            text: Texto a ser pré-processado
            
        Returns:
            Lista de tokens processados
        """
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        tokens_without_stopwords = self.remove_stopwords(tokens)
        stemmed_tokens = self.stem_tokens(tokens_without_stopwords)
        
        return stemmed_tokens
    
    def calculate_relevance_score(self, text: str, keywords: List[str]) -> float:
        """
        Calcula a pontuação de relevância de um texto com base em palavras-chave.
        
        Args:
            text: Texto a ser analisado
            keywords: Lista de palavras-chave para comparação
            
        Returns:
            Pontuação de relevância entre 0 e 1
        """
        if not text or not keywords:
            return 0.0
            
        # Pré-processar o texto
        processed_text = self.preprocess_text(text)
        
        # Pré-processar as palavras-chave
        processed_keywords = []
        for keyword in keywords:
            processed_keywords.extend(self.preprocess_text(keyword))
        
        # Contar ocorrências de palavras-chave no texto
        keyword_count = sum(1 for token in processed_text if token in processed_keywords)
        
        # Calcular pontuação de relevância
        if not processed_text:
            return 0.0
            
        relevance_score = min(1.0, keyword_count / (len(processed_text) * 0.1))
        
        return relevance_score
    
    def extract_entities(self, text: str) -> List[str]:
        """
        Extrai entidades nomeadas do texto (versão simplificada).
        
        Args:
            text: Texto para extração de entidades
            
        Returns:
            Lista de possíveis entidades
        """
        # Esta é uma implementação simplificada
        # Para uma implementação completa, seria necessário usar um modelo de NER
        
        words = self.tokenize(text)
        # Considerar palavras capitalizadas como possíveis entidades
        entities = [word for word in words if word and word[0].isupper()]
        
        # Remover duplicatas
        unique_entities = list(set(entities))
        
        return unique_entities
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """
        Cria um resumo do texto selecionando as sentenças mais importantes.
        
        Args:
            text: Texto a ser resumido
            max_sentences: Número máximo de sentenças no resumo
            
        Returns:
            Texto resumido
        """
        if not text:
            return ""
            
        # Dividir o texto em sentenças
        sentences = nltk.sent_tokenize(text)
        
        if len(sentences) <= max_sentences:
            return text
            
        # Calcular a frequência das palavras
        words = self.tokenize(text)
        words = self.remove_stopwords(words)
        
        word_freq = {}
        for word in words:
            if word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] += 1
        
        # Calcular a pontuação de cada sentença
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            sentence_words = self.tokenize(sentence)
            sentence_words = self.remove_stopwords(sentence_words)
            
            score = sum(word_freq.get(word, 0) for word in sentence_words)
            sentence_scores[i] = score
        
        # Selecionar as sentenças com maior pontuação
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:max_sentences]
        top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Ordenar por posição original
        
        # Construir o resumo
        summary = ' '.join(sentences[i] for i, _ in top_sentences)
        
        return summary
