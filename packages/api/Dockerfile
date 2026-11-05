FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY packages/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 --retries 5 -r requirements.txt

# Descargar recursos de NLTK necesarios
RUN python -m nltk.downloader stopwords

# Copiar módulos de la aplicación, pipeline de NLP y artefactos del modelo
COPY packages/ /app/packages/
COPY models/ /app/models/

# Variables de entorno
ENV PYTHONPATH=/app/packages:/app
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
