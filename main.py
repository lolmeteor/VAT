"""
Главное приложение FastAPI для VAT (Voice Analysis Tool)
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.api import auth, files, analyses, webhooks, user

# Создаем таблицы при запуске (если их нет)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

# Создаем приложение FastAPI
app = FastAPI(
    title="VAT - Voice Analysis Tool",
    description="Сервис транскрибации и анализа аудиофайлов",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins.split(",") if settings.cors_allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(user.router, prefix="/api")

# Обработчик глобальных ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Внутренняя ошибка сервера",
            "detail": str(exc) if settings.app_env == "development" else "Обратитесь в поддержку"
        }
    )

# Корневой эндпоинт
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "VAT API работает",
        "version": "1.0.0",
        "environment": settings.app_env
    }

# Эндпоинт для проверки здоровья приложения
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-01-16T12:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development"
    )
