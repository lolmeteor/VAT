"""
Главное приложение FastAPI для VAT (Voice Analysis Tool)
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.api import auth, files, analyses, webhooks, user, common

# ──────────────────────────── Логирование ──────────────────────────────
logging.basicConfig(
    level=logging.INFO, 
    format="%(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ──────────────────────── Lifespan (startup/shutdown) ───────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создаём/обновляем структуру БД при запуске сервера."""
    logger.info("Запуск VAT backend… создаём таблицы, если их нет…")
    Base.metadata.create_all(bind=engine)  # если используете Alembic, удалите
    yield
    logger.info("Остановка VAT backend…")

# ─────────────────────────────── App ────────────────────────────────────
app = FastAPI(
    title="VAT – Voice Analysis Tool",
    description="Сервис транскрибации и анализа аудиофайлов",
    version="1.0.0",
    lifespan=lifespan,
)

# ─────────────────────────────── CORS ───────────────────────────────────
origins = (
    settings.cors_allowed_origins.split(",")
    if settings.cors_allowed_origins != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────── Роутеры API ───────────────────────────────
for router in (common, auth, user, files, analyses, webhooks):
    app.include_router(router.router, prefix="/api")

# ─────────────────────── Глобальный обработчик ошибок ──────────────────
@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Внутренняя ошибка сервера",
            "detail": str(exc) if settings.app_env == "development" else "Обратитесь в поддержку",
        },
    )

# ─────────────────────────── Служебные эндпоинты ────────────────────────
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "VAT API работает",
        "version": "1.0.0",
        "environment": settings.app_env,
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "VAT API",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

# ─────────────────────────────── main ───────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development",
        log_level="info",
    )
