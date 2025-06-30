"""
API эндпоинты для общих запросов (health check, root)
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Проверка состояния сервиса
    """
    return {"status": "healthy"}

@router.get("/")
async def root():
    """
    Корневой эндпоинт API
    """
    return {
        "success": True,
        "message": "VAT API работает",
        "version": "1.0.0",
        "environment": "production"
    }
