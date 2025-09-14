from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine, settings
from .routers import auth, finance, reports
from . import models

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Manager API", version="1.0.0")

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(finance.router)
app.include_router(reports.router)

# Serve frontend (PWA) at /
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
