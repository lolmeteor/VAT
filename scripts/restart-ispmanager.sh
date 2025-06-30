#!/bin/bash

echo "=== Перезапуск ISPmanager ==="

# Останавливаем все связанные процессы
echo "1. Останавливаем все процессы ISPmanager..."
systemctl stop ispmgr 2>/dev/null
systemctl stop ispmgr-core 2>/dev/null
pkill -f ispmgr 2>/dev/null
sleep 3

# Проверяем что процессы остановлены
echo "2. Проверяем что процессы остановлены..."
if ps aux | grep -i ispmgr | grep -v grep; then
    echo "Принудительно завершаем оставшиеся процессы..."
    pkill -9 -f ispmgr 2>/dev/null
    sleep 2
fi

# Очищаем временные файлы
echo "3. Очищаем временные файлы..."
rm -f /usr/local/mgr5/var/*.pid 2>/dev/null
rm -f /tmp/ispmgr* 2>/dev/null

# Запускаем ISPmanager
echo "4. Запускаем ISPmanager..."
systemctl start ispmgr 2>/dev/null || {
    echo "Systemctl не сработал, запускаем вручную..."
    /usr/local/mgr5/sbin/ispmgr --daemon
}

# Ждем запуска
echo "5. Ждем запуска (10 секунд)..."
sleep 10

# Проверяем результат
echo "6. Проверяем результат..."
if netstat -tlnp | grep -q :1500; then
    echo "✅ ISPmanager успешно запущен на порту 1500"
    echo "🌐 Доступ: https://$(hostname -I | awk '{print $1}'):1500"
else
    echo "❌ ISPmanager не запустился"
    echo "Проверяем логи..."
    tail -10 /usr/local/mgr5/var/ispmgr.log 2>/dev/null || echo "Лог файл не найден"
fi

echo -e "\n=== Конец перезапуска ==="
