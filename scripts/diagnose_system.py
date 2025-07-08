#!/usr/bin/env python3
"""
Скрипт для диагностики системы VAT
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import User, AudioFile, Transcription, Analysis
import json
from datetime import datetime

def diagnose_database():
    """Диагностика базы данных"""
    print("=== ДИАГНОСТИКА БАЗЫ ДАННЫХ ===")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Проверяем подключение к БД
        result = db.execute(text("SELECT 1")).fetchone()
        print("✅ Подключение к БД: OK")
        
        # Проверяем таблицы
        tables = ['users', 'audio_files', 'transcriptions', 'analyses']
        for table in tables:
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"📊 Таблица {table}: {count} записей")
        
        # Последние загруженные файлы
        print("\n=== ПОСЛЕДНИЕ АУДИОФАЙЛЫ ===")
        files = db.query(AudioFile).order_by(AudioFile.created_at.desc()).limit(5).all()
        for file in files:
            print(f"🎵 {file.file_id}: {file.original_file_name} - {file.status}")
            
            # Проверяем транскрипцию для каждого файла
            transcription = db.query(Transcription).filter(Transcription.file_id == file.file_id).first()
            if transcription:
                print(f"   📝 Транскрипция: {transcription.status}")
                print(f"   📝 ID: {transcription.transcription_id}")
                print(f"   📝 Текст: {'Есть' if transcription.transcription_text else 'Нет'}")
                print(f"   📝 S3 ссылка: {'Есть' if transcription.s3_link_text else 'Нет'}")
                
                # Проверяем анализы
                analyses = db.query(Analysis).filter(Analysis.transcription_id == transcription.transcription_id).all()
                print(f"   🔍 Анализов: {len(analyses)}")
                for analysis in analyses:
                    print(f"      - {analysis.analysis_type}: {analysis.status}")
                    if analysis.error_message:
                        print(f"        ❌ Ошибка: {analysis.error_message}")
            else:
                print("   ❌ Транскрипция не найдена")
            print()
        
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
    finally:
        db.close()

def diagnose_api_endpoints():
    """Диагностика API эндпоинтов"""
    print("\n=== ДИАГНОСТИКА API ===")
    
    import requests
    base_url = "https://www.vertexassistant.ru/api"
    
    endpoints = [
        "/health",
        "/",
        "/analyses/types/available",
        "/user/tariffs"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", verify=False, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def diagnose_s3_connection():
    """Диагностика S3 подключения"""
    print("\n=== ДИАГНОСТИКА S3 ===")
    
    try:
        from app.services.s3 import S3Service
        s3_service = S3Service()
        
        # Пробуем получить список объектов
        response = s3_service.client.list_objects_v2(
            Bucket=settings.s3_bucket_name,
            MaxKeys=5
        )
        
        print("✅ S3 подключение: OK")
        print(f"📊 Объектов в бакете: {response.get('KeyCount', 0)}")
        
        if 'Contents' in response:
            print("📁 Последние файлы:")
            for obj in response['Contents'][:3]:
                print(f"   - {obj['Key']} ({obj['Size']} байт)")
                
    except Exception as e:
        print(f"❌ S3 ошибка: {e}")

def diagnose_make_webhooks():
    """Диагностика Make.com вебхуков"""
    print("\n=== ДИАГНОСТИКА MAKE.COM ===")
    
    print(f"🔗 Транскрипция webhook: {settings.make_transcription_webhook_url}")
    print(f"🔗 Анализ webhooks: {len(settings.make_analysis_webhooks)} настроено")
    
    for analysis_type, webhook_url in settings.make_analysis_webhooks.items():
        print(f"   - {analysis_type}: {webhook_url[:50]}...")

def main():
    print("🔍 ДИАГНОСТИКА СИСТЕМЫ VAT")
    print("=" * 50)
    
    diagnose_database()
    diagnose_api_endpoints()
    diagnose_s3_connection()
    diagnose_make_webhooks()
    
    print("\n" + "=" * 50)
    print("✅ Диагностика завершена")

if __name__ == "__main__":
    main()
