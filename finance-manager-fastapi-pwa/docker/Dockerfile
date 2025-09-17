# Multi-stage build: backend with FastAPI+Uvicorn
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy source
COPY backend /app/backend
COPY frontend /app/frontend

# Create data dir for SQLite (mounted volume at runtime)
RUN mkdir -p /data

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
