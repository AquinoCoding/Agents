"""
Arquivo de configuração para o projeto de agentes de IA.
Contém configurações para os modelos, APIs e parâmetros gerais.
"""

# Configurações do Ollama
OLLAMA_CONFIG = {
    "model": "gemma",  # Modelo padrão
    "host": "http://localhost",  # Host do Ollama
    "port": 11434,  # Porta padrão do Ollama
    "timeout": 60,  # Timeout em segundos
}

# Configurações para os agentes de coleta
AGENT_CONFIG = {
    # Configurações para o agente do G1
    "g1": {
        "base_url": "https://g1.globo.com",
        "categories": ["politica", "economia", "entretenimento"],
        "max_articles": 10,
    },
    
    # Configurações para o agente do Twitter
    "twitter": {
        "search_terms": ["política", "entretenimento", "notícias"],
        "max_tweets": 50,
        "result_type": "popular",
    },
    
    # Configurações para o agente do Instagram
    "instagram": {
        "profiles": ["g1", "bbcbrasil", "cnnbrasil"],
        "hashtags": ["noticia", "politica", "entretenimento"],
        "max_posts": 20,
    }
}

# Configurações para processamento de dados
PROCESSING_CONFIG = {
    "min_relevance_score": 0.6,
    "max_content_length": 1000,
    "language": "pt-br",
}

# Configurações para geração de matérias
CONTENT_GENERATION_CONFIG = {
    "min_words": 500,
    "max_paragraphs": 5,
    "temperature": 0.7,
    "top_p": 0.9,
}

# Configurações para métricas e insights
METRICS_CONFIG = {
    "engagement_threshold": 0.5,
    "trending_threshold": 0.7,
    "sentiment_analysis": True,
}

# Configurações de saída
OUTPUT_CONFIG = {
    "json_output_path": "data/processed/materias.json",
    "metrics_output_path": "data/processed/metricas.json",
}
