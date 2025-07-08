#!/usr/bin/env python3
"""
Прямое тестирование создания анализа в БД
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis, Transcription, AudioFile, AnalysisType, ProcessingStatus
import uuid

def test_create_analysis():
    """Тестирование создания анализа напрямую в БД"""
    print("=== ТЕСТ СОЗДАНИЯ АНАЛИЗА ===")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Находим завершенную транскрипцию
        transcription = db.query(Transcription).filter(
            Transcription.status == ProcessingStatus.completed
        ).first()
        
        if not transcription:
            print("❌ Нет завершенных транскрипций для тестирования")
            return
            
        print(f"✅ Найдена транскрипция: {transcription.transcription_id}")
        print(f"📝 Статус: {transcription.status}")
        print(f"📝 Есть текст: {'Да' if transcription.transcription_text else 'Нет'}")
        print(f"📝 S3 ссылка: {'Да' if transcription.s3_link_text else 'Нет'}")
        
        # Создаем тестовый анализ
        analysis = Analysis(
            analysis_id=str(uuid.uuid4()),
            transcription_id=transcription.transcription_id,
            analysis_type=AnalysisType.kp,  # ИСПРАВЛЕНО: используем lowercase
            status=ProcessingStatus.pending
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        print(f"✅ Анализ создан: {analysis.analysis_id}")
        print(f"📊 Тип: {analysis.analysis_type}")
        print(f"📊 Статус: {analysis.status}")
        
        # Проверяем, что анализ сохранился
        saved_analysis = db.query(Analysis).filter(
            Analysis.analysis_id == analysis.analysis_id
        ).first()
        
        if saved_analysis:
            print("✅ Анализ успешно сохранен в БД")
        else:
            print("❌ Анализ не найден в БД")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_create_analysis()
