#!/bin/bash

echo "=== Исправление ISPmanager ==="

# Останавливаем все процессы ISPmanager
echo "1. Останавливаем процессы ISPmanager..."
pkill -f ispmgr 2>/dev/null || echo "Процессы не найдены"

# Проверяем и исправляем права доступа
echo "2. Проверяем права доступа..."
if [ -d /usr/local/mgr5 ]; then
    chown -R root:root /usr/local/mgr5
    chmod +x /usr/local/mgr5/sbin/mgrctl
    chmod +x /usr/local/mgr5/sbin/ispmgr
fi

# Проверяем конфигурацию MySQL в ISPmanager
echo "3. Проверяем конфигурацию базы данных..."
if [ -f /usr/local/mgr5/etc/ispmgr.conf ]; then
    # Создаем резервную копию
    cp /usr/local/mgr5/etc/ispmgr.conf /usr/local/mgr5/etc/ispmgr.conf.backup.$(date +%Y%m%d_%H%M%S)
    
    # Проверяем настройки MySQL
    grep -q "DbHost" /usr/local/mgr5/etc/ispmgr.conf || echo "DbHost 127.0.0.1" >> /usr/local/mgr5/etc/ispmgr.conf
    grep -q "DbPort" /usr/local/mgr5/etc/ispmgr.conf || echo "DbPort 3306" >> /usr/local/mgr5/etc/ispmgr.conf
fi

# Пытаемся запустить ISPmanager
echo "4. Запускаем ISPmanager..."
systemctl start ispmgr 2>/dev/null || /usr/local/mgr5/sbin/ispmgr &

# Ждем несколько секунд
sleep 5

# Проверяем результат
echo "5. Проверяем результат..."
if netstat -tlnp | grep -q :1500; then
    echo "✅ ISPmanager успешно запущен на порту 1500"
else
    echo "❌ ISPmanager не запустился"
    echo "Попробуем запустить в режиме отладки..."
    /usr/local/mgr5/sbin/ispmgr --debug
fi

echo -e "\n=== Конец исправления ==="
