FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY Backend/requirements.txt ./

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY Backend/ ./Backend/

EXPOSE 8000

CMD ["uvicorn", "Backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
