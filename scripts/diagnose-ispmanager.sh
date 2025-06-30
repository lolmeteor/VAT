#!/bin/bash

echo "=== Диагностика ISPmanager ==="

# Проверяем статус ISPmanager
echo "1. Статус сервисов ISPmanager:"
systemctl status ispmgr 2>/dev/null || echo "Сервис ispmgr не найден"
systemctl status ispmgr-core 2>/dev/null || echo "Сервис ispmgr-core не найден"

# Проверяем процессы
echo -e "\n2. Процессы ISPmanager:"
ps aux | grep -i ispmgr | grep -v grep || echo "Процессы ISPmanager не найдены"

# Проверяем порты
echo -e "\n3. Порты ISPmanager (обычно 1500):"
netstat -tlnp | grep :1500 || echo "Порт 1500 не прослушивается"

# Проверяем логи
echo -e "\n4. Последние ошибки в логах ISPmanager:"
if [ -f /usr/local/mgr5/var/ispmgr.log ]; then
    tail -20 /usr/local/mgr5/var/ispmgr.log | grep -i error
else
    echo "Лог файл не найден"
fi

# Проверяем конфигурацию
echo -e "\n5. Конфигурация ISPmanager:"
if [ -f /usr/local/mgr5/etc/ispmgr.conf ]; then
    echo "Файл конфигурации найден"
    grep -E "^(path|user|group)" /usr/local/mgr5/etc/ispmgr.conf 2>/dev/null || echo "Основные параметры не найдены"
else
    echo "Файл конфигурации не найден"
fi

# Проверяем MySQL подключение для ISPmanager
echo -e "\n6. Проверка подключения к MySQL:"
mysql -h127.0.0.1 -P3306 -utranscr -ptranscr123 -e "SHOW DATABASES;" 2>/dev/null && echo "MySQL доступен" || echo "Проблема с подключением к MySQL"

# Проверяем права доступа
echo -e "\n7. Права доступа к директориям ISPmanager:"
ls -la /usr/local/mgr5/ | head -5
ls -la /usr/local/mgr5/sbin/mgrctl 2>/dev/null || echo "mgrctl не найден"

echo -e "\n=== Конец диагностики ==="
