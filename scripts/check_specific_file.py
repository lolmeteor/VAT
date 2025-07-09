#!/usr/bin/env python3
"""
Проверка конкретного файла
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis, Transcription, AudioFile, User

def check_file():
    """Проверка конкретного файла"""
    print("=== ПРОВЕРКА ФАЙЛА 06dd9e5d-df00-44d4-8fbd-6f7c23898de5 ===")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        file_id = '06dd9e5d-df00-44d4-8fbd-6f7c23898de5'
        
        # Проверяем аудиофайл
        audio_file = db.query(AudioFile).filter(AudioFile.file_id == file_id).first()
        if audio_file:
            print(f"✅ Аудиофайл найден:")
            print(f"   File ID: {audio_file.file_id}")
            print(f"   Название: {audio_file.original_file_name}")
            print(f"   User ID: {audio_file.user_id}")
            print(f"   Статус: {audio_file.status}")
            print(f"   Создан: {audio_file.created_at}")
        else:
            print("❌ Аудиофайл не найден")
            return
        
        # Проверяем транскрипцию
        transcription = db.query(Transcription).filter(Transcription.file_id == file_id).first()
        if transcription:
            print(f"\n✅ Транскрипция найдена:")
            print(f"   Transcription ID: {transcription.transcription_id}")
            print(f"   Статус: {transcription.status}")
            print(f"   Есть текст: {'Да' if transcription.transcription_text else 'Нет'}")
            print(f"   S3 ссылка: {'Да' if transcription.s3_link_text else 'Нет'}")
            print(f"   Создана: {transcription.created_at}")
            
            # Проверяем анализы
            analyses = db.query(Analysis).filter(Analysis.transcription_id == transcription.transcription_id).all()
            print(f"\n📊 Анализов для этой транскрипции: {len(analyses)}")
            
            for analysis in analyses:
                print(f"   - {analysis.analysis_type}: {analysis.status} ({analysis.created_at})")
                if analysis.analysis_text:
                    print(f"     Есть результат: {len(analysis.analysis_text)} символов")
                else:
                    print(f"     Результата нет")
        else:
            print("\n❌ Транскрипция не найдена")
            print("Создаем транскрипцию...")
            
            # Создаем транскрипцию
            import uuid
            from app.models import ProcessingStatus
            
            transcription = Transcription(
                transcription_id=str(uuid.uuid4()),
                file_id=file_id,
                status=ProcessingStatus.pending
            )
            
            db.add(transcription)
            db.commit()
            db.refresh(transcription)
            
            print(f"✅ Транскрипция создана: {transcription.transcription_id}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_file()
