"""
API роутеры для аутентификации пользователей
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth import AuthService
from app.schemas import TelegramAuthData, ApiResponse, UserResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram", response_model=UserResponse)
async def telegram_auth(
    auth_data: TelegramAuthData,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя через Telegram
    """
    try:
        auth_service = AuthService(db)
        
        # Проверяем подпись Telegram
        if not auth_service.verify_telegram_auth(auth_data):
            raise HTTPException(status_code=400, detail="Неверная подпись Telegram")
        
        # Создаем или обновляем пользователя
        user = auth_service.get_or_create_user(auth_data)
        
        # Создаем сессию
        session_id = auth_service.create_session(
            user.user_id,
            request.headers.get("user-agent"),
            request.client.host if request.client else None
        )
        
        # Устанавливаем cookie с сессией
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=30 * 24 * 60 * 60,  # 30 дней
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        return user
        
    except Exception as e:
        logger.error(f"Ошибка авторизации через Telegram: {e}")
        raise HTTPException(status_code=500, detail="Ошибка авторизации")

@router.post("/logout", response_model=ApiResponse)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Выход из системы
    """
    try:
        session_id = request.cookies.get("session_id")
        if session_id:
            auth_service = AuthService(db)
            # Удаляем сессию из БД
            from app.models import Session as UserSession
            session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
        
        # Удаляем cookie
        response.delete_cookie("session_id")
        
        return ApiResponse(success=True, message="Успешный выход")
        
    except Exception as e:
        logger.error(f"Ошибка при выходе: {e}")
        raise HTTPException(status_code=500, detail="Ошибка выхода")

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Получение информации о текущем пользователе
    """
    try:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=401, detail="Не авторизован")
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_session(session_id)
        
        if not user:
            raise HTTPException(status_code=401, detail="Сессия недействительна")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")
