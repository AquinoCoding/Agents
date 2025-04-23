FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos do projeto
COPY . /app/

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Expor porta para API (opcional)
EXPOSE 8000

# Criar diretórios de dados
RUN mkdir -p data/raw data/processed/insights data/processed/visualizations

# Script de inicialização
RUN echo '#!/bin/bash\n\
# Iniciar o serviço Ollama em background\n\
ollama serve &\n\
sleep 5\n\
\n\
# Baixar o modelo Gemma se não existir\n\
if ! ollama list | grep -q "gemma"; then\n\
    echo "Baixando modelo Gemma..."\n\
    ollama pull gemma\n\
fi\n\
\n\
# Executar o comando passado para o contêiner\n\
exec "$@"\n\
' > /app/docker-entrypoint.sh

RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando padrão (pode ser substituído na linha de comando)
CMD ["python", "main.py"]
