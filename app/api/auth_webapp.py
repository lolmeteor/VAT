"""
API эндпоинт для авторизации через Telegram Web App
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth import AuthService
from app.schemas import UserResponse, ApiResponse
from pydantic import BaseModel
import hashlib
import hmac
import urllib.parse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

class WebAppAuthData(BaseModel):
    initData: str

def verify_telegram_webapp_data(init_data: str, bot_token: str) -> dict:
    """
    Проверяет подлинность данных от Telegram Web App
    """
    try:
        # Парсим данные
        parsed_data = urllib.parse.parse_qs(init_data)
        
        # Извлекаем hash
        received_hash = parsed_data.get('hash', [None])[0]
        if not received_hash:
            raise ValueError("Hash отсутствует")
        
        # Создаем строку для проверки (исключаем hash)
        data_check_arr = []
        for key, values in parsed_data.items():
            if key != 'hash':
                data_check_arr.append(f"{key}={values[0]}")
        
        data_check_arr.sort()
        data_check_string = '\n'.join(data_check_arr)
        
        # Вычисляем ожидаемый hash
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        # Проверяем hash
        if not hmac.compare_digest(expected_hash, received_hash):
            raise ValueError("Неверная подпись")
        
        # Парсим данные пользователя
        user_data = parsed_data.get('user', [None])[0]
        if user_data:
            import json
            user_info = json.loads(user_data)
            return user_info
        
        raise ValueError("Данные пользователя отсутствуют")
        
    except Exception as e:
        logger.error(f"Ошибка валидации Web App данных: {e}")
        raise ValueError(f"Ошибка валидации: {str(e)}")

@router.post("/telegram-webapp", response_model=UserResponse)
async def telegram_webapp_auth(
    auth_data: WebAppAuthData,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Авторизация через Telegram Web App
    """
    try:
        from app.config import settings
        
        # Валидируем данные Web App
        user_info = verify_telegram_webapp_data(auth_data.initData, settings.telegram_bot_token)
        
        # Создаем объект данных авторизации
        from app.schemas import TelegramAuthData
        telegram_auth_data = TelegramAuthData(
            id=user_info['id'],
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
            username=user_info.get('username'),
            photo_url=user_info.get('photo_url'),
            auth_date=int(user_info.get('auth_date', 0)),
            hash="webapp_validated"  # Специальный маркер
        )
        
        auth_service = AuthService(db)
        
        # Создаем или обновляем пользователя
        user = auth_service.get_or_create_user(telegram_auth_data)
        
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
        logger.error(f"Ошибка Web App авторизации: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {str(e)}")
