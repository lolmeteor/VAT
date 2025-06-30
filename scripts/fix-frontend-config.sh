#!/bin/bash

echo "=== Исправление конфигурации Frontend ==="

# Переходим в директорию проекта
cd /opt/vat

# Создаем правильный .env.local файл
echo "1. Создаем правильный .env.local..."
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_BASE_URL=https://www.vertexassistant.ru/api
NEXT_PUBLIC_TELEGRAM_BOT_NAME=VertexAIassistantBOT
EOF

echo "2. Проверяем содержимое .env.local:"
cat .env.local

# Пересобираем Next.js приложение
echo "3. Пересобираем Next.js приложение..."
source venv/bin/activate
pnpm run build

# Перезапускаем сервисы
echo "4. Перезапускаем сервисы..."
systemctl restart vat-frontend
sleep 3
systemctl restart vat-fastapi

echo "5. Проверяем статус:"
systemctl status vat-frontend --no-pager -l | head -5

echo "✅ Конфигурация исправлена"
echo "🌐 Проверьте сайт: https://www.vertexassistant.ru"
