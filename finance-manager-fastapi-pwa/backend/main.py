from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .settings import settings
from .db import engine, Base, get_db
from .auth import get_password_hash
from .utils import ensure_superuser, suggestions
from . import models

from .routers import crud_routes, report_routes, sync_routes
from .routers import auth_token, user_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend (PWA) from /
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota raiz -> retorna o frontend
@app.get("/")
async def read_index():
    index_path = os.path.join("static", "index.html")
    return FileResponse(index_path)

@app.get("/health")
def health():
    return {"status": "ok"}

# Create first superuser if not exists
@app.on_event("startup")
def startup_seed():
    with next(get_db()) as db:
        ensure_superuser(db, settings.FIRST_SUPERUSER_EMAIL, get_password_hash(settings.FIRST_SUPERUSER_PASSWORD))

# Routers
app.include_router(auth_token.router)
app.include_router(user_routes.router)
app.include_router(crud_routes.router)
app.include_router(report_routes.router)
app.include_router(sync_routes.router)

@app.get("/api/suggestions")
def get_suggestions(user: models.User = Depends(__import__('backend.auth', fromlist=['get_current_user']).get_current_user), db: Session = Depends(get_db)):
    return suggestions(db, user.id)
