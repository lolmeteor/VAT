-- ВНИМАНИЕ: Этот скрипт удалит все существующие таблицы и данные!
-- Используйте только если вы уверены, что хотите начать с чистой базы данных.

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Отключаем проверку внешних ключей для безопасного удаления таблиц
SET FOREIGN_KEY_CHECKS = 0;

-- Удаляем таблицы, если они существуют (в правильном порядке)
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `analyses`;
DROP TABLE IF EXISTS `transcriptions`;
DROP TABLE IF EXISTS `audio_files`;
DROP TABLE IF EXISTS `sessions`;
DROP TABLE IF EXISTS `users`;

-- Включаем обратно проверку внешних ключей
SET FOREIGN_KEY_CHECKS = 1;

-- Создание таблиц заново
SOURCE schema-fixed.sql;

COMMIT;
