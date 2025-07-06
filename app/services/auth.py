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
        bot_token = settings.telegram_bot_token
        
        auth_dict = auth_data.dict(exclude={'hash'})
        auth_dict = {k: v for k, v in auth_dict.items() if v is not None}
        
        check_string = "\n".join([
            f"{key}={value}" 
            for key, value in sorted(auth_dict.items())
        ])
        
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(expected_hash, auth_data.hash)
    
    def get_or_create_user(self, auth_data: TelegramAuthData) -> UserResponse:
        user = self.db.query(User).filter(User.telegram_id == auth_data.id).first()
        
        if not user:
            user = User(
                user_id=str(uuid.uuid4()),
                telegram_id=auth_data.id,
                username=auth_data.username,
                first_name=auth_data.first_name,
                last_name=auth_data.last_name,
                balance_minutes=90,
                agreed_to_personal_data=True,
                agreed_to_terms=True,
                onboarding_completed=False
            )
            self.db.add(user)
        else:
            user.username = auth_data.username
            user.first_name = auth_data.first_name
            user.last_name = auth_data.last_name
        
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.from_orm(user)
    
    def create_session(self, user_id: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=30)
        
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
        session = self.db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        user = self.db.query(User).filter(User.user_id == session.user_id).first()
        return UserResponse.from_orm(user) if user else None
