#!/usr/bin/env python3
"""
Симуляция завершения анализа от Make.com для тестирования
"""
import sys
import os
sys.path.append('/opt/vat')

import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis, ProcessingStatus

def simulate_analysis_completion():
    """Симулируем завершение анализа"""
    print("=== СИМУЛЯЦИЯ ЗАВЕРШЕНИЯ АНАЛИЗА ===")
    
    # Подключаемся к БД
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Находим анализ в статусе processing
        analysis = db.query(Analysis).filter(
            Analysis.status == ProcessingStatus.processing
        ).first()
        
        if not analysis:
            print("❌ Нет анализов в статусе 'processing'")
            return
            
        print(f"✅ Найден анализ: {analysis.analysis_id}")
        print(f"📊 Тип: {analysis.analysis_type}")
        
        # Симулируем результат от ИИ
        fake_analysis_result = {
            "analysis_text": f"""
АНАЛИЗ ТИПА: {analysis.analysis_type.value.upper()}

Это тестовый анализ, сгенерированный системой для проверки работоспособности.

ОСНОВНЫЕ ВЫВОДЫ:
1. Транскрипция успешно обработана
2. Анализ выполнен согласно заданным параметрам
3. Система работает корректно

РЕКОМЕНДАЦИИ:
- Продолжить тестирование других типов анализа
- Проверить качество генерируемых документов
- Убедиться в корректности webhook'ов

Дата анализа: {analysis.created_at}
Тип анализа: {analysis.analysis_type.value}
            """.strip(),
            
            "analysis_summary": f"Тестовый анализ типа '{analysis.analysis_type.value}' выполнен успешно. Система работает корректно.",
            
            "key_points": [
                "Транскрипция обработана успешно",
                "Анализ выполнен согласно параметрам", 
                "Система функционирует корректно",
                f"Тип анализа: {analysis.analysis_type.value}"
            ]
        }
        
        # Обновляем анализ в БД (как это делал бы Make.com)
        analysis.analysis_text = fake_analysis_result["analysis_text"]
        analysis.analysis_summary = fake_analysis_result["analysis_summary"]
        analysis.key_points = fake_analysis_result["key_points"]
        analysis.status = ProcessingStatus.completed
        
        db.commit()
        print("✅ Анализ обновлен в БД")
        
        # Отправляем webhook завершения (как это делал бы Make.com)
        webhook_data = {
            "analysis_id": analysis.analysis_id,
            "status": "completed"
        }
        
        response = requests.post(
            "https://www.vertexassistant.ru/api/webhooks/analysis/completed",
            json=webhook_data,
            verify=False,
            timeout=10
        )
        
        print(f"📡 Webhook отправлен: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        print(f"\n🎉 Анализ {analysis.analysis_id} завершен!")
        print("Теперь можете проверить результат в веб-интерфейсе")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_analysis_completion()
