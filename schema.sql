-- Финальная и полная схема базы данных

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `analyses`;
DROP TABLE IF EXISTS `transcriptions`;
DROP TABLE IF EXISTS `audio_files`;
DROP TABLE IF EXISTS `sessions`;
DROP TABLE IF EXISTS `tariffs`;
DROP TABLE IF EXISTS `users`;

SET FOREIGN_KEY_CHECKS = 1;

-- Таблица пользователей (Users)
CREATE TABLE `users` (
  `user_id` VARCHAR(36) NOT NULL,
  `telegram_id` BIGINT NOT NULL,
  `username` VARCHAR(255) NULL,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `balance_minutes` INT NOT NULL DEFAULT 0,
  `agreed_to_personal_data` BOOLEAN NOT NULL DEFAULT FALSE,
  `agreed_to_terms` BOOLEAN NOT NULL DEFAULT FALSE,
  `onboarding_completed` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица сессий (Sessions)
CREATE TABLE `sessions` (
  `session_id` VARCHAR(36) NOT NULL,
  `user_id` VARCHAR(36) NOT NULL,
  `user_agent` TEXT NULL,
  `ip_address` VARCHAR(45) NULL,
  `expires_at` TIMESTAMP NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица аудиофайлов (Audio Files)
CREATE TABLE `audio_files` (
  `file_id` VARCHAR(36) NOT NULL,
  `user_id` VARCHAR(36) NOT NULL,
  `original_file_name` VARCHAR(255) NOT NULL,
  `s3_link` VARCHAR(512) NOT NULL,
  `file_size_bytes` BIGINT NOT NULL,
  `duration_seconds` INT NULL,
  `status` ENUM('uploading', 'uploaded', 'processing_failed', 'deleted') NOT NULL DEFAULT 'uploading',
  `error_message` TEXT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица транскрибаций (Transcriptions)
CREATE TABLE `transcriptions` (
  `transcription_id` VARCHAR(36) NOT NULL,
  `file_id` VARCHAR(36) NOT NULL,
  `s3_link_text` VARCHAR(512) NULL,
  `transcription_text` LONGTEXT NULL,
  `speakers_count` INT NULL,
  `language_detected` VARCHAR(10) NULL,
  `status` ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  `error_message` TEXT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица анализов (Analyses)
CREATE TABLE `analyses` (
  `analysis_id` VARCHAR(36) NOT NULL,
  `transcription_id` VARCHAR(36) NOT NULL,
  `analysis_type` ENUM('kp', 'first_meeting', 'follow_up_meeting', 'protocol', 'speaker1_psycho', 'speaker1_negative', 'speaker2_psycho', 'speaker2_negative', 'speaker3_psycho', 'speaker3_negative', 'speaker4_psycho', 'speaker4_negative') NOT NULL,
  `s3_docx_link` VARCHAR(512) NULL,
  `s3_pdf_link` VARCHAR(512) NULL,
  `analysis_text` LONGTEXT NULL,
  `analysis_summary` TEXT NULL,
  `key_points` JSON NULL,
  `status` ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  `error_message` TEXT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица тарифов (Tariffs)
CREATE TABLE `tariffs` (
  `tariff_id` VARCHAR(50) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `minutes` INT NOT NULL,
  `price` DECIMAL(10, 2) NOT NULL,
  `currency` VARCHAR(3) NOT NULL DEFAULT 'RUB',
  `description` TEXT NULL,
  `is_popular` BOOLEAN NOT NULL DEFAULT FALSE,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Таблица платежей (Payments)
CREATE TABLE `payments` (
  `payment_id` VARCHAR(36) NOT NULL,
  `user_id` VARCHAR(36) NOT NULL,
  `tariff_id` VARCHAR(50) NULL,
  `amount` DECIMAL(10, 2) NOT NULL,
  `currency` VARCHAR(3) NOT NULL DEFAULT 'RUB',
  `minutes_added` INT NOT NULL,
  `status` ENUM('pending', 'succeeded', 'canceled') NOT NULL DEFAULT 'pending',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Первичные ключи
ALTER TABLE `users` ADD PRIMARY KEY (`user_id`), ADD UNIQUE KEY `telegram_id` (`telegram_id`);
ALTER TABLE `sessions` ADD PRIMARY KEY (`session_id`);
ALTER TABLE `audio_files` ADD PRIMARY KEY (`file_id`), ADD UNIQUE KEY `s3_link` (`s3_link`);
ALTER TABLE `transcriptions` ADD PRIMARY KEY (`transcription_id`), ADD UNIQUE KEY `file_id` (`file_id`);
ALTER TABLE `analyses` ADD PRIMARY KEY (`analysis_id`), ADD UNIQUE KEY `transcription_id_analysis_type` (`transcription_id`, `analysis_type`);
ALTER TABLE `tariffs` ADD PRIMARY KEY (`tariff_id`);
ALTER TABLE `payments` ADD PRIMARY KEY (`payment_id`);

-- Внешние ключи
ALTER TABLE `sessions` ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `audio_files` ADD CONSTRAINT `audio_files_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `transcriptions` ADD CONSTRAINT `transcriptions_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `audio_files` (`file_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `analyses` ADD CONSTRAINT `analyses_ibfk_1` FOREIGN KEY (`transcription_id`) REFERENCES `transcriptions` (`transcription_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `payments` ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `payments` ADD CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`tariff_id`) REFERENCES `tariffs` (`tariff_id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- Наполнение таблицы тарифов
INSERT INTO `tariffs` (`tariff_id`, `name`, `minutes`, `price`, `description`, `is_popular`) VALUES
('basic_300', 'Базовый пакет', 300, 500.00, 'Оптимальный выбор для регулярного использования', 0),
('popular_500', 'Популярный', 500, 800.00, 'Лучшее соотношение цены и качества', 1),
('maximum_2000', 'Максимальный', 2000, 2500.00, 'Для профессионального использования и команд', 0);

COMMIT;
