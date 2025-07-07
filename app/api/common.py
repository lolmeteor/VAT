"""
Общие API эндпоинты
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Проверка состояния API
    """
    return {
        "status": "healthy",
        "service": "VAT API",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """
    Корневой эндпоинт API
    """
    return {
        "success": True,
        "message": "VAT API работает",
        "version": "1.0.0",
        "docs": "/docs"
    }
