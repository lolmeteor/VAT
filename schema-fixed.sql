-- Устанавливаем режим SQL для совместимости и строгих проверок
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- =================================================================
-- Таблица пользователей (Users)
-- Хранит информацию о зарегистрированных пользователях.
-- =================================================================
CREATE TABLE `users` (
  `user_id` VARCHAR(36) NOT NULL COMMENT 'Уникальный идентификатор пользователя (UUID)',
  `telegram_id` BIGINT NOT NULL COMMENT 'Уникальный ID пользователя в Telegram',
  `username` VARCHAR(255) NULL COMMENT 'Имя пользователя (@username) в Telegram',
  `first_name` VARCHAR(255) NULL COMMENT 'Имя пользователя в Telegram',
  `last_name` VARCHAR(255) NULL COMMENT 'Фамилия пользователя в Telegram',
  `balance_minutes` INT NOT NULL DEFAULT 0 COMMENT 'Текущий баланс доступных минут для транскрибации',
  `agreed_to_personal_data` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Флаг согласия на обработку ПДн',
  `agreed_to_terms` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Флаг согласия с пользовательским соглашением',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время регистрации',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата и время последнего обновления записи'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- Таблица сессий (Sessions)
-- Хранит информацию об активных сессиях пользователей (для аутентификации).
-- =================================================================
CREATE TABLE `sessions` (
  `session_id` VARCHAR(36) NOT NULL COMMENT 'Уникальный идентификатор сессии (UUID)',
  `user_id` VARCHAR(36) NOT NULL COMMENT 'Ссылка на пользователя',
  `user_agent` TEXT NULL COMMENT 'User-Agent браузера пользователя',
  `ip_address` VARCHAR(45) NULL COMMENT 'IP-адрес пользователя',
  `expires_at` TIMESTAMP NOT NULL COMMENT 'Дата и время окончания срока действия сессии',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время создания сессии'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- Таблица аудиофайлов (Audio Files)
-- Хранит информацию о загруженных пользователями аудиофайлах.
-- =================================================================
CREATE TABLE `audio_files` (
  `file_id` VARCHAR(36) NOT NULL COMMENT 'Уникальный идентификатор файла (UUID)',
  `user_id` VARCHAR(36) NOT NULL COMMENT 'Ссылка на пользователя, загрузившего файл',
  `original_file_name` VARCHAR(255) NOT NULL COMMENT 'Оригинальное имя файла',
  `s3_link` VARCHAR(512) NOT NULL COMMENT 'Ссылка на файл в S3 хранилище',
  `file_size_bytes` BIGINT NOT NULL COMMENT 'Размер файла в байтах',
  `duration_seconds` INT NULL COMMENT 'Длительность аудио в секундах (определяется после обработки)',
  `status` ENUM('uploading', 'uploaded', 'processing_failed', 'deleted') NOT NULL DEFAULT 'uploading' COMMENT 'Статус загрузки файла',
  `error_message` TEXT NULL COMMENT 'Сообщение об ошибке, если загрузка не удалась',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время загрузки',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата и время последнего обновления'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- Таблица транскрибаций (Transcriptions)
-- Хранит результат и статус процесса транскрибации для каждого аудиофайла.
-- =================================================================
CREATE TABLE `transcriptions` (
  `transcription_id` VARCHAR(36) NOT NULL COMMENT 'Уникальный идентификатор транскрибации (UUID)',
  `file_id` VARCHAR(36) NOT NULL COMMENT 'Ссылка на аудиофайл',
  `s3_link_text` VARCHAR(512) NULL COMMENT 'Ссылка на текстовый файл (.txt) с результатом транскрибации в S3',
  `status` ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending' COMMENT 'Статус процесса транскрибации',
  `error_message` TEXT NULL COMMENT 'Сообщение об ошибке, если транскрибация не удалась',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время создания задачи',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата и время последнего обновления'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- Таблица анализов (Analyses)
-- Хранит результаты и статусы различных видов анализа для каждой транскрибации.
-- =================================================================
CREATE TABLE `analyses` (
  `analysis_id` VARCHAR(36) NOT NULL COMMENT 'Уникальный идентификатор анализа (UUID)',
  `transcription_id` VARCHAR(36) NOT NULL COMMENT 'Ссылка на транскрибацию',
  `analysis_type` ENUM('kp', 'first_meeting', 'follow_up_meeting', 'protocol', 'speaker1_psycho', 'speaker1_negative', 'speaker2_psycho', 'speaker2_negative', 'speaker3_psycho', 'speaker3_negative', 'speaker4_psycho', 'speaker4_negative') NOT NULL COMMENT 'Тип проведенного анализа',
  `s3_docx_link` VARCHAR(512) NULL COMMENT 'Ссылка на .docx отчет в S3',
  `s3_pdf_link` VARCHAR(512) NULL COMMENT 'Ссылка на .pdf отчет в S3',
  `status` ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending' COMMENT 'Статус процесса анализа',
  `error_message` TEXT NULL COMMENT 'Сообщение об ошибке, если анализ не удался',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время создания задачи',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата и время последнего обновления'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- Таблица платежей (Payments)
-- Хранит историю пополнений баланса пользователями через Юкассу.
-- =================================================================
CREATE TABLE `payments` (
  `payment_id` VARCHAR(36) NOT NULL COMMENT 'Уникальный идентификатор платежа (от Юкассы)',
  `user_id` VARCHAR(36) NOT NULL COMMENT 'Ссылка на пользователя, совершившего платеж',
  `amount` DECIMAL(10, 2) NOT NULL COMMENT 'Сумма платежа',
  `currency` VARCHAR(3) NOT NULL DEFAULT 'RUB' COMMENT 'Валюта платежа',
  `minutes_added` INT NOT NULL COMMENT 'Количество добавленных минут',
  `tariff_description` VARCHAR(255) NULL COMMENT 'Описание купленного тарифа/пакета',
  `status` ENUM('pending', 'succeeded', 'canceled') NOT NULL DEFAULT 'pending' COMMENT 'Статус платежа',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время создания платежа',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Дата и время последнего обновления статуса'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- Определение первичных ключей (Primary Keys)
-- =================================================================
ALTER TABLE `users` ADD PRIMARY KEY (`user_id`), ADD UNIQUE KEY `telegram_id` (`telegram_id`);
ALTER TABLE `sessions` ADD PRIMARY KEY (`session_id`);
ALTER TABLE `audio_files` ADD PRIMARY KEY (`file_id`), ADD UNIQUE KEY `s3_link` (`s3_link`);
ALTER TABLE `transcriptions` ADD PRIMARY KEY (`transcription_id`), ADD UNIQUE KEY `file_id` (`file_id`);
ALTER TABLE `analyses` ADD PRIMARY KEY (`analysis_id`), ADD UNIQUE KEY `transcription_id_analysis_type` (`transcription_id`, `analysis_type`);
ALTER TABLE `payments` ADD PRIMARY KEY (`payment_id`);

-- =================================================================
-- Определение внешних ключей (Foreign Keys)
-- Создаем связи между таблицами для обеспечения целостности данных.
-- =================================================================
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `audio_files`
  ADD CONSTRAINT `audio_files_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `transcriptions`
  ADD CONSTRAINT `transcriptions_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `audio_files` (`file_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `analyses`
  ADD CONSTRAINT `analyses_ibfk_1` FOREIGN KEY (`transcription_id`) REFERENCES `transcriptions` (`transcription_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;
