"""
SQLAlchemy модели для всех таблиц базы данных
"""
from sqlalchemy import Column, String, BigInteger, Integer, Text, TIMESTAMP, Enum, DECIMAL, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class AudioFileStatus(str, enum.Enum):
    uploading = "uploading"
    uploaded = "uploaded"
    processing_failed = "processing_failed"
    deleted = "deleted"

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisType(str, enum.Enum):
    KP = "kp"
    FIRST_MEETING = "first_meeting"
    FOLLOW_UP_MEETING = "follow_up_meeting"
    PROTOCOL = "protocol"
    SPEAKER1_PSYCHO = "speaker1_psycho"
    SPEAKER1_NEGATIVE = "speaker1_negative"
    SPEAKER2_PSYCHO = "speaker2_psycho"
    SPEAKER2_NEGATIVE = "speaker2_negative"
    SPEAKER3_PSYCHO = "speaker3_psycho"
    SPEAKER3_NEGATIVE = "speaker3_negative"
    SPEAKER4_PSYCHO = "speaker4_psycho"
    SPEAKER4_NEGATIVE = "speaker4_negative"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    balance_minutes = Column(Integer, nullable=False, default=0)
    agreed_to_personal_data = Column(Boolean, nullable=False, default=False)
    agreed_to_terms = Column(Boolean, nullable=False, default=False)
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audio_files = relationship("AudioFile", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    
    user = relationship("User", back_populates="sessions")

class AudioFile(Base):
    __tablename__ = "audio_files"
    
    file_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    s3_link = Column(String(512), unique=True, nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(Enum(AudioFileStatus), nullable=False, default=AudioFileStatus.UPLOADING)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    user = relationship("User", back_populates="audio_files")
    transcription = relationship("Transcription", back_populates="audio_file", uselist=False, cascade="all, delete-orphan")

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    transcription_id = Column(String(36), primary_key=True)
    file_id = Column(String(36), ForeignKey("audio_files.file_id"), unique=True, nullable=False)
    s3_link_text = Column(String(512), nullable=True)
    transcription_text = Column(Text, nullable=True)
    speakers_count = Column(Integer, nullable=True)
    language_detected = Column(String(10), nullable=True)
    status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    audio_file = relationship("AudioFile", back_populates="transcription")
    analyses = relationship("Analysis", back_populates="transcription", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"
    
    analysis_id = Column(String(36), primary_key=True)
    transcription_id = Column(String(36), ForeignKey("transcriptions.transcription_id"), nullable=False)
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    s3_docx_link = Column(String(512), nullable=True)
    s3_pdf_link = Column(String(512), nullable=True)
    analysis_text = Column(Text, nullable=True)
    analysis_summary = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)
    status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    transcription = relationship("Transcription", back_populates="analyses")

class Payment(Base):
    __tablename__ = "payments"
    
    payment_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    tariff_id = Column(String(50), ForeignKey("tariffs.tariff_id"), nullable=True) # Связь с тарифом
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="RUB")
    minutes_added = Column(Integer, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    user = relationship("User", back_populates="payments")
    tariff = relationship("Tariff")

class Tariff(Base):
    __tablename__ = "tariffs"
    
    tariff_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    minutes = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="RUB")
    description = Column(Text, nullable=True)
    is_popular = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
