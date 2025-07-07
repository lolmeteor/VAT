#!/bin/bash

echo "=== Перезапуск всех сервисов ==="

echo "1. Остановка сервисов..."
systemctl stop vat-fastapi
pm2 stop vat-frontend

echo "2. Очистка PM2..."
pm2 delete vat-frontend 2>/dev/null || true

echo "3. Запуск FastAPI..."
systemctl start vat-fastapi
sleep 3

echo "4. Запуск Next.js..."
cd /opt/vat
pm2 start npm --name vat-frontend -- run start

echo "5. Проверка статуса..."
systemctl status vat-fastapi --no-pager -l
pm2 status

echo "=== Перезапуск завершен ==="
