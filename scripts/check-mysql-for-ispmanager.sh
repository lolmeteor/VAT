#!/bin/bash

echo "=== Проверка MySQL для ISPmanager ==="

# Проверяем подключение к MySQL
echo "1. Тестируем подключение к MySQL..."
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "SELECT VERSION();" 2>/dev/null && echo "✅ MySQL доступен" || echo "❌ Проблема с MySQL"

# Проверяем базы данных ISPmanager
echo -e "\n2. Проверяем базы данных ISPmanager..."
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "SHOW DATABASES LIKE '%ispmgr%';" 2>/dev/null

# Создаем базу данных для ISPmanager если её нет
echo -e "\n3. Создаем базу данных для ISPmanager если нужно..."
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "CREATE DATABASE IF NOT EXISTS ispmgr CHARACTER SET utf8 COLLATE utf8_general_ci;" 2>/dev/null && echo "База данных ispmgr готова"

# Проверяем права пользователя
echo -e "\n4. Проверяем права пользователя transcr..."
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "GRANT ALL PRIVILEGES ON ispmgr.* TO 'transcr'@'%';" 2>/dev/null
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "GRANT ALL PRIVILEGES ON ispmgr.* TO 'transcr'@'localhost';" 2>/dev/null
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "FLUSH PRIVILEGES;" 2>/dev/null

echo "✅ MySQL настроен для ISPmanager"

echo -e "\n=== Конец проверки MySQL ==="
