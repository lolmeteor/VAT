#!/bin/bash

echo "=== ПРОВЕРКА ЛОГОВ VAT ==="

echo "1. Логи FastAPI (последние 50 строк):"
echo "----------------------------------------"
journalctl -u vat-fastapi -n 50 --no-pager

echo -e "\n2. Логи Nginx (последние 20 строк):"
echo "----------------------------------------"
tail -20 /var/log/nginx/vat_error.log

echo -e "\n3. Статус сервисов:"
echo "----------------------------------------"
systemctl status vat-fastapi --no-pager -l
pm2 status

echo -e "\n4. Проверка портов:"
echo "----------------------------------------"
ss -tlnp | grep -E "(3000|8000)"

echo -e "\n5. Тест API эндпоинтов:"
echo "----------------------------------------"
echo "Health check:"
curl -k -s https://www.vertexassistant.ru/api/health | jq '.' || echo "Ошибка"

echo -e "\nAnalyses types:"
curl -k -s https://www.vertexassistant.ru/api/analyses/types/available | jq '.' || echo "Ошибка"

echo -e "\n=== ПРОВЕРКА ЗАВЕРШЕНА ==="
