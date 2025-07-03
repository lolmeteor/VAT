-- Добавляем поле onboarding_completed в таблицу users
ALTER TABLE `users` 
ADD COLUMN `onboarding_completed` TINYINT(1) NOT NULL DEFAULT 0 
COMMENT 'Флаг завершения онбординга' 
AFTER `agreed_to_terms`;
