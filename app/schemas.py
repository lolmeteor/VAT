"""
Pydantic схемы для валидации данных API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import AudioFileStatus, ProcessingStatus, AnalysisType, PaymentStatus

# Базовые схемы для пользователя
class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    agreed_to_personal_data: bool = True
    agreed_to_terms: bool = True

class UserResponse(UserBase):
    user_id: str
    balance_minutes: int
    agreed_to_personal_data: bool
    agreed_to_terms: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для аудиофайлов
class AudioFileResponse(BaseModel):
    file_id: str
    original_file_name: str
    file_size_bytes: int
    duration_seconds: Optional[int]
    status: AudioFileStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для транскрибации
class TranscriptionResponse(BaseModel):
    transcription_id: str
    file_id: str
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для анализа
class AnalysisResponse(BaseModel):
    analysis_id: str
    transcription_id: str
    analysis_type: AnalysisType
    status: ProcessingStatus
    s3_docx_link: Optional[str]
    s3_pdf_link: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для платежей
class PaymentResponse(BaseModel):
    payment_id: str
    amount: float
    currency: str
    minutes_added: int
    tariff_description: Optional[str]
    status: PaymentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для запросов
class AnalysisRequest(BaseModel):
    transcription_id: str
    analysis_types: List[AnalysisType]

# ИСПРАВЛЕННАЯ схема для Telegram авторизации
class TelegramAuthData(BaseModel):
    id: int  # Telegram user ID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None # Добавлено это поле
    auth_date: int  # Unix timestamp
    hash: str  # Telegram signature

# Схемы для ответов API
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class UserStatsResponse(BaseModel):
    balance_minutes: int
    used_minutes: int
    analyses_completed: int
    files_uploaded: int
