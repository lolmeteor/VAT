#!/bin/bash

echo "=== Исправление конфигурации сервера ==="

# Переходим в директорию проекта
cd /opt/vat

echo "1. Обновляем конфигурационные файлы..."

# Создаем правильный .env.local для Next.js
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_BASE_URL=https://www.vertexassistant.ru/api
NEXT_PUBLIC_TELEGRAM_BOT_NAME=VertexAIassistantBOT
EOF

# Обновляем .env для Python (замените пароль на реальный)
cat > .env << 'EOF'
APP_ENV=production
APP_SECRET_KEY=aG3yL4zO2ryD2yQ8_VAT_SECRET_2025
APP_BASE_URL=https://www.vertexassistant.ru
CORS_ALLOWED_ORIGINS=https://www.vertexassistant.ru,https://www.vertexassistant.ru:443,https://vertexassistant.ru

DB_HOST=server268.hosting.reg.ru
DB_PORT=3306
DB_NAME=u3151465_VAT2
DB_USER=u3151465_Aleksey
DB_PASSWORD=YOUR_REAL_PASSWORD_HERE

TELEGRAM_BOT_TOKEN=7693655467:AAHMKYv6F8U5TVz-CPgNoOV-d52NgAETmp0
TELEGRAM_LOGIN_WIDGET_BOT_NAME=VertexAIassistantBOT

S3_ENDPOINT_URL=https://s3.regru.cloud
S3_ACCESS_KEY_ID=8TVU2GJ3DLFZVS5MUI3L
S3_SECRET_ACCESS_KEY=1ARu78H9fvqqDmDpDLJFVkVt0U5RQ1v8qlNdhpgb
S3_BUCKET_NAME=smartmashabot
S3_REGION=ru-central1

MAKE_TRANSCRIPTION_WEBHOOK_URL=https://hook.eu2.make.com/osl3us5x5bk8uqytihx73d8o24ebw57q
EOF

echo "2. Пересобираем Next.js приложение..."
source venv/bin/activate
npm run build

echo "3. Перезапускаем сервисы..."
systemctl restart vat-frontend
systemctl restart vat-fastapi
systemctl restart nginx

echo "4. Проверяем статус сервисов..."
sleep 5
systemctl status vat-frontend --no-pager -l | head -5
systemctl status vat-fastapi --no-pager -l | head -5

echo "5. Тестируем API..."
curl -k https://www.vertexassistant.ru/api/health

echo "✅ Конфигурация обновлена!"
echo "🌐 Проверьте сайт: https://www.vertexassistant.ru"
