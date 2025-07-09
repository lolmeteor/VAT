#!/usr/bin/env python3
"""
Тестирование API с авторизацией
"""
import sys
import os
sys.path.append('/opt/vat')

import requests
import json
from app.config import settings

def test_api_endpoints():
    """Тестирование API эндпоинтов"""
    print("=== ТЕСТИРОВАНИЕ API С АВТОРИЗАЦИЕЙ ===")
    
    base_url = "https://www.vertexassistant.ru/api"
    
    # Тестируем публичные эндпоинты
    public_endpoints = [
        "/health",
        "/",
        "/analyses/types/available",
        "/user/tariffs"
    ]
    
    print("📋 Публичные эндпоинты:")
    for endpoint in public_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", verify=False, timeout=10)
            print(f"   ✅ {endpoint}: {response.status_code}")
            if endpoint == "/analyses/types/available":
                data = response.json()
                if 'data' in data and 'types' in data['data']:
                    print(f"      Типов анализа: {len(data['data']['types'])}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    # Тестируем конкретный файл без авторизации
    file_id = "06dd9e5d-df00-44d4-8fbd-6f7c23898de5"
    print(f"\n📁 Тестирование файла {file_id}:")
    
    try:
        response = requests.get(f"{base_url}/files/{file_id}", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_api_endpoints()
