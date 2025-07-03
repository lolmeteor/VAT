"""
API эндпоинты для работы с пользователем
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.services.auth import AuthService
from app.models import User, AudioFile, Analysis, Payment
from app.schemas import UserStatsResponse, PaymentResponse, UserResponse, OnboardingStatusResponse, ApiResponse
from app.models import ProcessingStatus, PaymentStatus

router = APIRouter(prefix="/user", tags=["user"])

async def get_current_user_dependency(request: Request, db: Session = Depends(get_db)) -> UserResponse:
    """
    Dependency для получения текущего пользователя
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_session(session_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Сессия недействительна")
    
    return user

# ДОБАВЛЕНО: Эндпоинт для проверки статуса онбординга
@router.get("/onboarding-status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение статуса завершения онбординга
    """
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return OnboardingStatusResponse(onboarding_completed=bool(user.onboarding_completed))

# ДОБАВЛЕНО: Эндпоинт для завершения онбординга
@router.post("/complete-onboarding", response_model=ApiResponse)
async def complete_onboarding(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Отметка о завершении онбординга
    """
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.onboarding_completed = 1
    db.commit()
    
    return ApiResponse(success=True, message="Онбординг завершен")

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение статистики пользователя
    """
    # Подсчитываем статистику
    files_uploaded = db.query(func.count(AudioFile.file_id)).filter(
        AudioFile.user_id == current_user.user_id
    ).scalar() or 0
    
    analyses_completed = db.query(func.count(Analysis.analysis_id)).join(
        AudioFile, AudioFile.file_id == Analysis.transcription_id
    ).filter(
        AudioFile.user_id == current_user.user_id,
        Analysis.status == ProcessingStatus.COMPLETED
    ).scalar() or 0
    
    # Подсчитываем использованные минуты (примерная логика)
    # В реальности это должно учитывать длительность обработанных файлов
    used_minutes = db.query(func.sum(AudioFile.duration_seconds)).filter(
        AudioFile.user_id == current_user.user_id
    ).scalar() or 0
    used_minutes = int(used_minutes / 60) if used_minutes else 0
    
    return UserStatsResponse(
        balance_minutes=current_user.balance_minutes,
        used_minutes=used_minutes,
        analyses_completed=analyses_completed,
        files_uploaded=files_uploaded
    )

@router.get("/payments", response_model=list[PaymentResponse])
async def get_user_payments(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение истории платежей пользователя
    """
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.user_id
    ).order_by(Payment.created_at.desc()).all()
    
    return [PaymentResponse.from_orm(payment) for payment in payments]

@router.get("/tariffs")
async def get_available_tariffs():
    """
    Получение доступных тарифов
    """
    tariffs = [
        {
            "id": "free",
            "name": "Бесплатно",
            "minutes": 90,
            "price": 0,
            "currency": "RUB",
            "description": "Стартовый пакет для новых пользователей",
            "is_popular": False
        },
        {
            "id": "basic",
            "name": "Базовый пакет",
            "minutes": 300,
            "price": 500,
            "currency": "RUB",
            "description": "Оптимальный выбор для регулярного использования",
            "is_popular": False
        },
        {
            "id": "popular",
            "name": "Популярный",
            "minutes": 500,
            "price": 800,
            "currency": "RUB",
            "description": "Лучшее соотношение цены и качества",
            "is_popular": True
        },
        {
            "id": "maximum",
            "name": "Максимальный",
            "minutes": 2000,
            "price": 2500,
            "currency": "RUB",
            "description": "Для профессионального использования",
            "is_popular": False
        }
    ]
    
    return {
        "success": True,
        "data": {"tariffs": tariffs}
    }
