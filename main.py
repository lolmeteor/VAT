from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import common, auth, user, files, analyses, payments, webhooks
from app.config import settings

app = FastAPI(
    title="VAT - Voice Analysis Tool",
    description="Сервис транскрибации и анализа аудиофайлов",
    version="1.1.0",
)

origins = [
    "https://www.vertexassistant.ru",
    "https://www.vertexassistant.ru:443",
    "https://vertexassistant.ru",
    "https://vertexassistant.ru:443",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(common.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")

# Для запуска:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload