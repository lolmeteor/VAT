#!/bin/bash

echo "=== Проверка статуса сервисов ==="

echo "1. Проверка FastAPI (Backend):"
curl -s http://127.0.0.1:8000/api/health | jq '.' || echo "Backend недоступен"

echo -e "\n2. Проверка Next.js (Frontend):"
pm2 status | grep vat-frontend

echo -e "\n3. Проверка портов:"
ss -tlnp | grep -E "(3000|8000)"

echo -e "\n4. Проверка через HTTPS:"
curl -k -s https://www.vertexassistant.ru/api/health | jq '.' || echo "HTTPS недоступен"

echo -e "\n5. Проверка фронтенда через HTTPS:"
curl -k -s -I https://www.vertexassistant.ru/ | head -5

echo -e "\n=== Проверка завершена ==="
