"""
Cliente para interação com o Ollama.
Fornece métodos para carregar modelos e gerar conteúdo.
"""

import ollama
import logging
from typing import Dict, Any, Optional, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaClient:
    """Cliente para interação com modelos do Ollama."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o cliente Ollama.
        
        Args:
            config: Dicionário com configurações do Ollama
        """
        self.model = config.get("model", "gemma")
        self.host = config.get("host", "http://localhost")
        self.port = config.get("port", 11434)
        self.timeout = config.get("timeout", 60)
        
        # Configurar o cliente Ollama
        ollama.host = f"{self.host}:{self.port}"
        
        logger.info(f"Cliente Ollama inicializado com modelo {self.model}")
    
    def change_model(self, model_name: str) -> None:
        """
        Altera o modelo utilizado.
        
        Args:
            model_name: Nome do novo modelo
        """
        self.model = model_name
        logger.info(f"Modelo alterado para {model_name}")
    
    def list_models(self) -> List[str]:
        """
        Lista os modelos disponíveis no Ollama.
        
        Returns:
            Lista de nomes dos modelos disponíveis
        """
        try:
            models = ollama.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Gera texto usando o modelo atual.
        
        Args:
            prompt: Texto de entrada para o modelo
            temperature: Temperatura para geração (criatividade)
            max_tokens: Número máximo de tokens a serem gerados
            
        Returns:
            Texto gerado pelo modelo
        """
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )
            return response.get('response', '')
        except Exception as e:
            logger.error(f"Erro na geração de texto: {e}")
            return ""
    
    def analyze_content(self, content: str, instruction: str) -> str:
        """
        Analisa conteúdo com base em uma instrução específica.
        
        Args:
            content: Conteúdo a ser analisado
            instruction: Instrução para análise
            
        Returns:
            Resultado da análise
        """
        prompt = f"{instruction}\n\nConteúdo para análise:\n{content}"
        return self.generate(prompt)
    
    def extract_keywords(self, content: str, num_keywords: int = 5) -> List[str]:
        """
        Extrai palavras-chave de um conteúdo.
        
        Args:
            content: Conteúdo para extração de palavras-chave
            num_keywords: Número de palavras-chave a serem extraídas
            
        Returns:
            Lista de palavras-chave
        """
        prompt = f"Extraia exatamente {num_keywords} palavras-chave relevantes do seguinte texto, retornando apenas as palavras separadas por vírgula, sem explicações adicionais:\n\n{content}"
        response = self.generate(prompt)
        keywords = [kw.strip() for kw in response.split(',')]
        return keywords[:num_keywords]  # Garantir que temos exatamente o número solicitado
    
    def generate_article(self, 
                        topic: str, 
                        facts: List[str], 
                        min_words: int = 500, 
                        max_paragraphs: int = 5) -> Dict[str, Any]:
        """
        Gera uma matéria completa com base em um tópico e fatos.
        
        Args:
            topic: Tópico principal da matéria
            facts: Lista de fatos relevantes para a matéria
            min_words: Número mínimo de palavras
            max_paragraphs: Número máximo de parágrafos
            
        Returns:
            Dicionário com a matéria completa, incluindo título, subtítulo, etc.
        """
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        prompt = f"""
        Crie uma matéria jornalística completa sobre o seguinte tópico: {topic}
        
        Fatos importantes:
        {facts_text}
        
        Regras:
        - Seja objetivo, até {max_paragraphs} parágrafos
        - Mínimo de {min_words} palavras
        - Não use aspas
        - Crie título, subtítulo e editoria
        - Use foco no fato principal
        
        Formato de saída:
        Título: [título da matéria]
        Subtítulo: [subtítulo da matéria]
        Editoria: [editoria da matéria]
        
        [Corpo da matéria com {max_paragraphs} parágrafos]
        """
        
        response = self.generate(prompt, temperature=0.7, max_tokens=2000)
        
        # Processar a resposta para extrair as partes
        lines = response.strip().split('\n')
        
        titulo = ""
        subtitulo = ""
        editoria = ""
        corpo = ""
        
        for i, line in enumerate(lines):
            if line.startswith("Título:"):
                titulo = line.replace("Título:", "").strip()
            elif line.startswith("Subtítulo:"):
                subtitulo = line.replace("Subtítulo:", "").strip()
            elif line.startswith("Editoria:"):
                editoria = line.replace("Editoria:", "").strip()
            elif i > 3 and line.strip():  # Assumindo que as 3 primeiras linhas são título, subtítulo e editoria
                corpo += line + "\n"
        
        # Extrair palavras-chave do corpo da matéria
        keywords = self.extract_keywords(corpo)
        
        return {
            "materia": corpo.strip(),
            "titulo": titulo,
            "subtitulo": subtitulo,
            "editoria": editoria,
            "keywords": keywords
        }
