#!/usr/bin/env python3
"""
Тестирование эндпоинта анализов
"""
import sys
import os
sys.path.append('/opt/vat')

import requests
import json
from app.config import settings

def test_analyses_endpoint():
    """Тестирование эндпоинта /api/analyses/start"""
    print("=== ТЕСТИРОВАНИЕ ЭНДПОИНТА АНАЛИЗОВ ===")
    
    base_url = "https://www.vertexassistant.ru/api"
    
    # Тестовые данные
    test_data = {
        "transcription_id": "test-transcription-id",
        "analysis_types": ["kp", "first_meeting"]
    }
    
    print(f"🔗 URL: {base_url}/analyses/start")
    print(f"📝 Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/analyses/start",
            json=test_data,
            verify=False,
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_response = response.json()
                print(f"📋 JSON: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
            except:
                print("❌ Не удалось распарсить JSON")
                
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def check_router_registration():
    """Проверка регистрации роутеров"""
    print("\n=== ПРОВЕРКА РЕГИСТРАЦИИ РОУТЕРОВ ===")
    
    try:
        from main import app
        
        print("📋 Зарегистрированные роуты:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if '/analyses' in route.path:
                    print(f"   ✅ {route.methods} {route.path}")
                    
    except Exception as e:
        print(f"❌ Ошибка проверки роутеров: {e}")

if __name__ == "__main__":
    test_analyses_endpoint()
    check_router_registration()
