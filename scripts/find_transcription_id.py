#!/usr/bin/env python3
"""
Поиск правильного transcription_id для файла
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis, Transcription, AudioFile

def find_transcription_for_file():
    """Находим transcription_id для конкретного файла"""
    print("=== ПОИСК TRANSCRIPTION_ID ===")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Файлы из URL в браузере
        file_ids = [
            'afb8e9bd-ff1f-4e46-90d9-fa5902a2d958',  # из последнего URL
            '853e9aab-d63f-4aae-9b66-3fbdb8d1d701',  # из первого URL  
            '9d464a13-eda6-4654-be5e-78d1516e0f08',  # из логов
            'd66d0cb3-902e-46fb-af6c-abfae7d4f7dc'   # из логов
        ]
        
        for file_id in file_ids:
            print(f"\n🔍 Проверяем файл: {file_id}")
            
            # Ищем аудиофайл
            audio_file = db.query(AudioFile).filter(AudioFile.file_id == file_id).first()
            if not audio_file:
                print("   ❌ Аудиофайл не найден")
                continue
                
            print(f"   ✅ Файл: {audio_file.original_file_name}")
            print(f"   📅 Создан: {audio_file.created_at}")
            
            # Ищем транскрипцию
            transcription = db.query(Transcription).filter(Transcription.file_id == file_id).first()
            if not transcription:
                print("   ❌ Транскрипция не найдена")
                continue
                
            print(f"   📝 Transcription ID: {transcription.transcription_id}")
            print(f"   📊 Статус: {transcription.status}")
            
            # Ищем анализы
            analyses = db.query(Analysis).filter(Analysis.transcription_id == transcription.transcription_id).all()
            print(f"   🔍 Анализов: {len(analyses)}")
            
            for analysis in analyses:
                print(f"      - {analysis.analysis_type.value}: {analysis.status.value}")
                print(f"        ID: {analysis.analysis_id}")
                if analysis.analysis_summary:
                    print(f"        Есть результат: {len(analysis.analysis_summary)} символов")
            
            # Генерируем curl команду для тестирования
            if transcription:
                print(f"\n🧪 Тест команда:")
                print(f'curl -k -s "https://www.vertexassistant.ru/api/analyses/transcription/{transcription.transcription_id}" \\')
                print(f'  -H "Cookie: session_id=a58e4354-ee8b-470b-a0e1-166b0160502a" | jq \'.\'')
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    find_transcription_for_file()
