"""
Pydantic схемы для валидации данных API
"""
from pydantic import BaseModel, Field, computed_field
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
    # ДОБАВЛЕНО: Поле для отслеживания завершения онбординга
    onboarding_completed: bool
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

    @computed_field
    @property
    def download_url_txt(self) -> Optional[str]:
        if self.status == ProcessingStatus.COMPLETED:
            return f"/api/files/{self.file_id}/transcription/download/txt"
        return None

    @computed_field
    @property
    def download_url_docx(self) -> Optional[str]:
        if self.status == ProcessingStatus.COMPLETED:
            return f"/api/files/{self.file_id}/transcription/download/docx"
        return None
    
    class Config:
        from_attributes = True

# Схемы для анализа
class AnalysisResponse(BaseModel):
    analysis_id: str
    transcription_id: str
    analysis_type: AnalysisType
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def download_url_docx(self) -> Optional[str]:
        if self.status == ProcessingStatus.COMPLETED:
            return f"/api/analyses/{self.analysis_id}/download/docx"
        return None

    @computed_field
    @property
    def download_url_pdf(self) -> Optional[str]:
        # Генерация PDF пока не реализована, но можно оставить заглушку
        if self.status == ProcessingStatus.COMPLETED:
            return f"/api/analyses/{self.analysis_id}/download/pdf"
        return None
    
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

# ДОБАВЛЕНО: Схема для статуса онбординга
class OnboardingStatusResponse(BaseModel):
    onboarding_completed: bool

class TranscriptionWebhookData(BaseModel):
    file_id: str
    status: str  # "completed" или "failed"
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None

class AnalysisWebhookData(BaseModel):
    analysis_id: str
    status: str  # "completed" или "failed"
    error_message: Optional[str] = None
