#!/usr/bin/env python3
"""
Проверка структуры БД
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine, text
from app.config import settings

def check_db_structure():
    """Проверяем структуру таблиц"""
    print("=== ПРОВЕРКА СТРУКТУРЫ БД ===")
    
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            # Проверяем структуру таблицы payments
            result = conn.execute(text("DESCRIBE payments"))
            print("📊 Структура таблицы payments:")
            for row in result:
                print(f"   {row[0]} - {row[1]}")
            
            print("\n📊 Все таблицы в БД:")
            result = conn.execute(text("SHOW TABLES"))
            for row in result:
                print(f"   {row[0]}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_db_structure()
