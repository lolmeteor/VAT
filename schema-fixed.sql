-- Создание базы данных VAT
CREATE DATABASE IF NOT EXISTS vat_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vat_db;

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    balance_minutes INT NOT NULL DEFAULT 0,
    agreed_to_personal_data TINYINT(1) NOT NULL DEFAULT 0,
    agreed_to_terms TINYINT(1) NOT NULL DEFAULT 0,
    onboarding_completed TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Таблица сессий
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(45),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Таблица аудиофайлов
CREATE TABLE IF NOT EXISTS audio_files (
    file_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    original_file_name VARCHAR(255) NOT NULL,
    s3_link VARCHAR(512) UNIQUE NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    duration_seconds INT,
    status ENUM('uploading', 'uploaded', 'processing_failed', 'deleted') NOT NULL DEFAULT 'uploading',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Таблица транскрипций
CREATE TABLE IF NOT EXISTS transcriptions (
    transcription_id VARCHAR(36) PRIMARY KEY,
    file_id VARCHAR(36) UNIQUE NOT NULL,
    s3_link_text VARCHAR(512),
    transcription_text TEXT,
    speakers_count INT,
    language_detected VARCHAR(10),
    status ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES audio_files(file_id) ON DELETE CASCADE
);

-- Таблица анализов
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id VARCHAR(36) PRIMARY KEY,
    transcription_id VARCHAR(36) NOT NULL,
    analysis_type ENUM('kp', 'first_meeting', 'follow_up_meeting', 'protocol', 'speaker1_psycho', 'speaker1_negative', 'speaker2_psycho', 'speaker2_negative', 'speaker3_psycho', 'speaker3_negative', 'speaker4_psycho', 'speaker4_negative') NOT NULL,
    s3_docx_link VARCHAR(512),
    s3_pdf_link VARCHAR(512),
    analysis_text TEXT,
    analysis_summary TEXT,
    key_points JSON,
    status ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (transcription_id) REFERENCES transcriptions(transcription_id) ON DELETE CASCADE
);

-- Таблица платежей
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'RUB',
    minutes_added INT NOT NULL,
    tariff_description VARCHAR(255),
    status ENUM('pending', 'succeeded', 'canceled') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Индексы для оптимизации
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_audio_files_user_id ON audio_files(user_id);
CREATE INDEX idx_audio_files_status ON audio_files(status);
CREATE INDEX idx_transcriptions_file_id ON transcriptions(file_id);
CREATE INDEX idx_transcriptions_status ON transcriptions(status);
CREATE INDEX idx_analyses_transcription_id ON analyses(transcription_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
