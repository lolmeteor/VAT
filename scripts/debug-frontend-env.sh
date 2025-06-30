#!/bin/bash

echo "=== Отладка переменных окружения Frontend ==="

cd /opt/vat

echo "1. Содержимое .env.local:"
if [ -f .env.local ]; then
    cat .env.local
else
    echo "❌ Файл .env.local не найден!"
fi

echo ""
echo "2. Содержимое .env:"
if [ -f .env ]; then
    cat .env | head -10
else
    echo "❌ Файл .env не найден!"
fi

echo ""
echo "3. Проверяем процесс Next.js:"
ps aux | grep next

echo ""
echo "4. Проверяем логи frontend:"
journalctl -u vat-frontend --no-pager -l | tail -10

echo ""
echo "5. Тестируем API напрямую:"
curl -k https://www.vertexassistant.ru/api/health

echo ""
echo "✅ Отладка завершена"
