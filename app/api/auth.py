"""
API эндпоинты для аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth import AuthService
from app.schemas import TelegramAuthData, UserResponse, ApiResponse
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/telegram", response_model=UserResponse)
async def telegram_login(
    auth_data: TelegramAuthData,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    if not auth_service.verify_telegram_auth(auth_data):
        raise HTTPException(status_code=400, detail="Неверные данные аутентификации")
    
    user = auth_service.get_or_create_user(auth_data)
    
    session_id = auth_service.create_session(
        user_id=user.user_id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=30 * 24 * 60 * 60,  # 30 дней
        httponly=True,
        secure=settings.app_env == "production", # True для HTTPS, False для HTTP
        samesite="lax"
    )
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_session(session_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Сессия недействительна")
    
    return user

@router.post("/logout", response_model=ApiResponse)
async def logout(response: Response):
    response.delete_cookie("session_id")
    return ApiResponse(success=True, message="Успешный выход из системы")
