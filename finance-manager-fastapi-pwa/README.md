# Finance Manager (FastAPI + PWA)

Aplicação minimalista para gestão de finanças pessoais com API REST (FastAPI), sincronização offline (IndexedDB + outbox), PWA responsivo e relatórios básicos com Chart.js.

## Desenvolvimento local
```bash
cp .env.example .env
docker compose up -d --build
# Acesse http://localhost:8000/static/index.html
```
Login: use as credenciais do `.env` (FIRST_SUPERUSER_EMAIL / FIRST_SUPERUSER_PASSWORD).
