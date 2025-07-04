"""
Главное приложение FastAPI для VAT (Voice Analysis Tool)
Продакшн конфигурация
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.api import auth, files, analyses, webhooks, user, common

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="VAT - Voice Analysis Tool",
    description="Сервис транскрибации и анализа аудиофайлов",
    version="1.0.0",
    lifespan=lifespan
)

# Исправляем CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.vertexassistant.ru",
        "https://www.vertexassistant.ru:443",
        "https://vertexassistant.ru",
        "https://vertexassistant.ru:443"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(common.router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Внутренняя ошибка сервера",
            "detail": "Обратитесь в поддержку"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
