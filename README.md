# Sistema de Agentes de IA para Consumo de Conteúdo

Este projeto implementa um sistema de agentes de IA para consumir conteúdos de diversas fontes (G1, Twitter, Instagram) e gerar matérias relevantes em formato JSON.

## Estrutura do Projeto

```
ai_news_agent/
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── g1_agent.py
│   │   ├── twitter_agent.py
│   │   ├── instagram_agent.py
│   ├── models/
│   │   ├── ollama_client.py
│   ├── utils/
│   │   ├── text_processor.py
│   ├── api/
│   ├── config/
│   │   ├── config.py
│   ├── agent_orchestrator.py
│   ├── data_processor.py
│   ├── insight_generator.py
│   ├── content_generator.py
│   ├── test_ollama.py
├── data/
│   ├── raw/
│   ├── processed/
│       ├── insights/
│       ├── visualizations/
├── main.py
├── validate_results.py
├── setup_ollama.sh
```

## Requisitos

- Python 3.10+
- Ollama (com modelo Gemma)
- Bibliotecas Python: requests, beautifulsoup4, pandas, nltk, transformers, tqdm, ollama, tweepy, instaloader

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual Python:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```
   pip install requests beautifulsoup4 pandas nltk transformers tqdm ollama tweepy instaloader
   ```
4. Instale o Ollama e baixe o modelo Gemma:
   ```
   chmod +x setup_ollama.sh
   ./setup_ollama.sh
   ```

## Uso

### Executar o pipeline completo

```
python main.py
```

### Executar etapas específicas

```
python main.py --step collect  # Apenas coleta de dados
python main.py --step process  # Apenas processamento de dados
python main.py --step insights  # Apenas geração de insights
python main.py --step generate  # Apenas geração de matérias
```

### Executar coleta de dados de um agente específico

```
python main.py --step collect --agent g1
python main.py --step collect --agent twitter
python main.py --step collect --agent instagram
```

### Validar resultados

```
python validate_results.py --all  # Validar todos os resultados
python validate_results.py --articles  # Validar apenas as matérias
python validate_results.py --insights  # Validar apenas os insights
```

## Componentes Principais

### Agentes de Coleta

- **G1Agent**: Coleta notícias do portal G1 usando web scraping
- **TwitterAgent**: Utiliza a API do Twitter para coletar tweets relevantes
- **InstagramAgent**: Usa Instaloader para coletar posts do Instagram

### Processamento de Dados

- **DataProcessor**: Processa, filtra e consolida os dados coletados
- **InsightGenerator**: Gera insights, métricas e visualizações
- **ContentGenerator**: Gera matérias em formato JSON usando o modelo Gemma via Ollama

### Formato das Matérias Geradas

```json
{
  "materia": "Texto da matéria com pelo menos 500 palavras",
  "editoria": "Categoria da matéria",
  "subtitulo": "Subtítulo da matéria",
  "titulo": "Título da matéria",
  "keywords": ["palavra-chave1", "palavra-chave2"]
}
```

## Configuração

As configurações do sistema estão no arquivo `src/config/config.py` e incluem:

- Configurações do Ollama (modelo, host, porta)
- Configurações dos agentes de coleta (fontes, termos de busca)
- Configurações de processamento de dados
- Configurações de geração de conteúdo

## Notas

- O sistema foi projetado para ser modular e extensível
- Novos agentes de coleta podem ser adicionados implementando a interface BaseAgent
- O modelo Gemma pode ser substituído por outros modelos disponíveis no Ollama
