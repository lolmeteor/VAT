"""
Сервис аутентификации через Telegram Login Widget
"""
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, Session as UserSession
from app.schemas import TelegramAuthData, UserCreate, UserResponse
from app.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def verify_telegram_auth(self, auth_data: TelegramAuthData) -> bool:
        """
        Проверяет подлинность данных от Telegram Login Widget
        """
        bot_token = settings.telegram_bot_token
        
        # ОТЛАДОЧНЫЕ ЛОГИ
        print(f"🔍 Проверка Telegram auth для пользователя: {auth_data.id}")
        print(f"🔑 Bot token (первые 10 символов): {bot_token[:10]}...")
        print(f"📝 Полученные данные: {auth_data.dict()}")
        
        # Создаем строку для проверки подписи (ИСКЛЮЧАЕМ hash)
        auth_dict = auth_data.dict(exclude={'hash'})
        # Убираем None значения
        auth_dict = {k: v for k, v in auth_dict.items() if v is not None}
        
        check_string = "\n".join([
            f"{key}={value}" 
            for key, value in sorted(auth_dict.items())
        ])
        
        print(f"📝 Check string: {check_string}")
        
        # Вычисляем ожидаемый хеш
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        
        print(f"🔐 Expected hash: {expected_hash}")
        print(f"🔐 Received hash: {auth_data.hash}")
        
        result = hmac.compare_digest(expected_hash, auth_data.hash)
        print(f"✅ Verification result: {result}")
        
        return result
    
    def get_or_create_user(self, auth_data: TelegramAuthData) -> UserResponse:
        """
        Получает существующего пользователя или создает нового
        """
        # Ищем пользователя по telegram_id
        user = self.db.query(User).filter(User.telegram_id == auth_data.id).first()
        
        if not user:
            # Создаем нового пользователя с 90 бесплатными минутами
            user_data = UserCreate(
                telegram_id=auth_data.id,
                username=auth_data.username,
                first_name=auth_data.first_name,
                last_name=auth_data.last_name,
                agreed_to_personal_data=True,
                agreed_to_terms=True
            )
            
            user = User(
                user_id=str(uuid.uuid4()),
                telegram_id=user_data.telegram_id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                balance_minutes=90,  # Стартовые бесплатные минуты
                agreed_to_personal_data=user_data.agreed_to_personal_data,
                agreed_to_terms=user_data.agreed_to_terms
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Обновляем информацию о пользователе из Telegram
            user.username = auth_data.username
            user.first_name = auth_data.first_name
            user.last_name = auth_data.last_name
            self.db.commit()
        
        return UserResponse.from_orm(user)
    
    def create_session(self, user_id: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> str:
        """
        Создает новую сессию для пользователя
        """
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=30)  # Сессия на 30 дней
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )
        
        self.db.add(session)
        self.db.commit()
        
        return session_id
    
    def get_user_by_session(self, session_id: str) -> Optional[UserResponse]:
        """
        Получает пользователя по ID сессии
        """
        session = self.db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        user = self.db.query(User).filter(User.user_id == session.user_id).first()
        return UserResponse.from_orm(user) if user else None
