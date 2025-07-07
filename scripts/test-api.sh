#!/bin/bash

echo "=== Тестирование API эндпоинтов ==="

BASE_URL="https://www.vertexassistant.ru/api"

echo "1. Health check:"
curl -k -s "$BASE_URL/health" | jq '.'

echo -e "\n2. Root endpoint:"
curl -k -s "$BASE_URL/" | jq '.'

echo -e "\n3. Available tariffs:"
curl -k -s "$BASE_URL/user/tariffs" | jq '.'

echo -e "\n4. Analysis types:"
curl -k -s "$BASE_URL/analyses/types/available" | jq '.'

echo -e "\n=== Тестирование завершено ==="
