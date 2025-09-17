# Finance Web Service (FastAPI + PWA)

- API: FastAPI + SQLAlchemy (SQLite by default)
- Frontend: PWA vanilla (Chart.js) com fila offline e sincronização manual
- Auth: OAuth2 + JWT (básico)

## Rodando local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Abra http://localhost:8000

## Docker
```bash
docker build -t finance-fastapi .
docker run -p 8000:8000 -v $(pwd)/data:/app -e SECRET_KEY=supersecret finance-fastapi
```

## Endpoints principais
- `POST /api/auth/register`
- `POST /api/auth/token`
- `GET/POST /api/categories`
- `GET/POST /api/transactions`
- `POST /api/sync/push`
- `GET /api/reports/summary`
