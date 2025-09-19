FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Criar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (opcional, dependendo das libs)
RUN apt-get update && apt-get install -y build-essential libpq-dev curl

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar backend
COPY backend /app/backend

# Copiar frontend atualizado para pasta /app/static
COPY frontend /app/static

# Expor porta do Uvicorn
EXPOSE 8000

# Rodar aplicação
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

