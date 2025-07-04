#!/bin/bash

echo "=== Исправление конфигурации с ПРАВИЛЬНЫМИ данными ==="

# Переходим в директорию проекта
cd /opt/vat

echo "1. Обновляем .env файл с правильными данными БД и S3..."

# Создаем правильный .env файл с ВАШИМИ данными
cat > .env << 'EOF'
# Продакшн переменные окружения
APP_ENV=production
APP_SECRET_KEY=aG3yL4zO2ryD2yQ8_VAT_SECRET_2025
APP_BASE_URL=https://www.vertexassistant.ru
CORS_ALLOWED_ORIGINS=https://www.vertexassistant.ru,https://www.vertexassistant.ru:443,https://vertexassistant.ru

# База данных - ЛОКАЛЬНАЯ MySQL 5.7 в Docker (ВАШИ ДАННЫЕ)
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=vat_db
DB_USER=transcr
DB_PASSWORD=transcr123

# Telegram
TELEGRAM_BOT_TOKEN=7693655467:AAHMKYv6F8U5TVz-CPgNoOV-d52NgAETmp0
TELEGRAM_LOGIN_WIDGET_BOT_NAME=VertexAIassistantBOT

# S3 Reg.ru - ПРАВИЛЬНЫЙ БАКЕТ vatbucket
S3_ENDPOINT_URL=https://s3.regru.cloud
S3_ACCESS_KEY_ID=8TVU2GJ3DLFZVS5MUI3L
S3_SECRET_ACCESS_KEY=1ARu78H9fvqqDmDpDLJFVkVt0U5RQ1v8qlNdhpgb
S3_BUCKET_NAME=vatbucket
S3_REGION=ru-central1

# Make.com
MAKE_TRANSCRIPTION_WEBHOOK_URL=https://hook.eu2.make.com/osl3us5x5bk8uqytihx73d8o24ebw57q
EOF

echo "2. Обновляем .env.local для Next.js..."
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_BASE_URL=https://www.vertexassistant.ru/api
NEXT_PUBLIC_TELEGRAM_BOT_NAME=VertexAIassistantBOT
EOF

echo "3. Проверяем что MySQL контейнер работает..."
docker ps | grep mysql || echo "❌ MySQL контейнер не запущен!"

echo "4. Тестируем подключение к S3 бакету vatbucket..."
python3 -c "
import boto3
import os
from dotenv import load_dotenv
load_dotenv()

try:
    s3_client = boto3.client(
        's3',
        endpoint_url='https://s3.regru.cloud',
        aws_access_key_id='8TVU2GJ3DLFZVS5MUI3L',
        aws_secret_access_key='1ARu78H9fvqqDmDpDLJFVkVt0U5RQ1v8qlNdhpgb',
        region_name='ru-central1'
    )
    response = s3_client.list_objects_v2(Bucket='vatbucket', MaxKeys=5)
    print('✅ Подключение к S3 бакету vatbucket успешно')
    if 'Contents' in response:
        print(f'📁 Найдено файлов в бакете: {len(response[\"Contents\"])}')
    else:
        print('📁 Бакет пустой')
except Exception as e:
    print(f'❌ Ошибка S3: {e}')
"

echo "5. Пересобираем Next.js приложение..."
source venv/bin/activate
npm run build

echo "6. Перезапускаем сервисы..."
systemctl restart vat-frontend
systemctl restart vat-fastapi
systemctl restart nginx

echo "7. Проверяем статус..."
sleep 5
systemctl status vat-frontend --no-pager -l | head -5
systemctl status vat-fastapi --no-pager -l | head -5

echo "8. Тестируем подключение к БД..."
python3 -c "
import pymysql
try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='transcr', password='transcr123', database='vat_db')
    print('✅ Подключение к БД успешно')
    conn.close()
except Exception as e:
    print(f'❌ Ошибка БД: {e}')
"

echo "9. Тестируем API..."
curl -k https://www.vertexassistant.ru/api/health

echo "✅ Конфигурация исправлена с правильными данными!"
echo "📦 S3 бакет: vatbucket"
echo "🗄️ БД: vat_db (transcr/transcr123)"
echo "🌐 Проверьте сайт: https://www.vertexassistant.ru"
