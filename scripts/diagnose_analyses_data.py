#!/usr/bin/env python3
"""
Диагностика данных анализов в БД
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis, Transcription, AudioFile, User
from datetime import datetime, timedelta
import json

def diagnose_analyses_data():
    """Диагностика данных анализов"""
    print("=== ДИАГНОСТИКА ДАННЫХ АНАЛИЗОВ ===")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Общая статистика
        total_analyses = db.query(Analysis).count()
        print(f"📊 Всего анализов в БД: {total_analyses}")
        
        # Анализы по статусам
        print("\n📈 Анализы по статусам:")
        statuses = db.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM analyses 
            GROUP BY status 
            ORDER BY count DESC
        """)).fetchall()
        
        for status, count in statuses:
            print(f"   {status}: {count}")
        
        # Анализы по типам
        print("\n📋 Анализы по типам:")
        types = db.execute(text("""
            SELECT analysis_type, COUNT(*) as count 
            FROM analyses 
            GROUP BY analysis_type 
            ORDER BY count DESC
        """)).fetchall()
        
        for analysis_type, count in types:
            print(f"   {analysis_type}: {count}")
        
        # Анализы по времени создания
        print("\n⏰ Анализы по времени:")
        now = datetime.utcnow()
        
        time_ranges = [
            ("Последние 5 минут", 5),
            ("Последние 30 минут", 30),
            ("Последний час", 60),
            ("Последние 24 часа", 24 * 60),
            ("Старше 24 часов", None)
        ]
        
        for label, minutes in time_ranges:
            if minutes:
                cutoff = now - timedelta(minutes=minutes)
                count = db.query(Analysis).filter(Analysis.created_at >= cutoff).count()
            else:
                cutoff = now - timedelta(hours=24)
                count = db.query(Analysis).filter(Analysis.created_at < cutoff).count()
            
            print(f"   {label}: {count}")
        
        # Детальный анализ по файлам
        print("\n📁 Анализы по файлам (топ 10):")
        file_analyses = db.execute(text("""
            SELECT 
                af.file_id,
                af.original_file_name,
                af.user_id,
                COUNT(a.analysis_id) as analyses_count,
                MIN(a.created_at) as first_analysis,
                MAX(a.created_at) as last_analysis
            FROM audio_files af
            LEFT JOIN transcriptions t ON af.file_id = t.file_id
            LEFT JOIN analyses a ON t.transcription_id = a.transcription_id
            WHERE a.analysis_id IS NOT NULL
            GROUP BY af.file_id, af.original_file_name, af.user_id
            ORDER BY analyses_count DESC
            LIMIT 10
        """)).fetchall()
        
        for row in file_analyses:
            file_id, filename, user_id, count, first, last = row
            print(f"   📄 {filename[:30]}...")
            print(f"      File ID: {file_id}")
            print(f"      User ID: {user_id}")
            print(f"      Анализов: {count}")
            print(f"      Первый: {first}")
            print(f"      Последний: {last}")
            print()
        
        # Поиск дублирующих анализов
        print("🔍 Поиск дублирующих анализов:")
        duplicates = db.execute(text("""
            SELECT 
                transcription_id,
                analysis_type,
                COUNT(*) as count
            FROM analyses
            GROUP BY transcription_id, analysis_type
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)).fetchall()
        
        if duplicates:
            print(f"   Найдено {len(duplicates)} групп дублирующих анализов:")
            for transcription_id, analysis_type, count in duplicates[:10]:
                print(f"   - {analysis_type} для {transcription_id}: {count} дублей")
        else:
            print("   ✅ Дублирующих анализов не найдено")
        
        # Анализы без результатов
        print("\n❌ Анализы без результатов:")
        empty_analyses = db.query(Analysis).filter(
            Analysis.analysis_text.is_(None),
            Analysis.analysis_summary.is_(None),
            Analysis.key_points.is_(None)
        ).count()
        print(f"   Анализов без данных: {empty_analyses}")
        
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_analyses_data()
