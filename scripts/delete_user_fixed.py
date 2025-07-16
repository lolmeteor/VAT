#!/usr/bin/env python3
"""
Исправленный скрипт удаления пользователя
"""
import sys
import os
sys.path.append('/opt/vat')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

def delete_user_completely(user_id: str):
    print(f"=== УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ {user_id} ===")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Находим пользователя через прямой SQL запрос
        user_result = db.execute(text("SELECT * FROM users WHERE user_id = :user_id"), {"user_id": user_id}).fetchone()
        if not user_result:
            print(f"❌ Пользователь {user_id} не найден")
            return
        
        print(f"✅ Найден пользователь:")
        print(f"   Telegram ID: {user_result.telegram_id}")
        print(f"   Username: @{user_result.username}" if user_result.username else "   Username: не указан")
        print(f"   Имя: {user_result.first_name or ''} {user_result.last_name or ''}")
        print(f"   Создан: {user_result.created_at}")
        
        # Подсчитываем связанные данные через SQL
        sessions_count = db.execute(text("SELECT COUNT(*) FROM sessions WHERE user_id = :user_id"), {"user_id": user_id}).scalar()
        audio_files_count = db.execute(text("SELECT COUNT(*) FROM audio_files WHERE user_id = :user_id"), {"user_id": user_id}).scalar()
        
        # Проверяем, есть ли таблица payments и какие в ней колонки
        try:
            payments_count = db.execute(text("SELECT COUNT(*) FROM payments WHERE user_id = :user_id"), {"user_id": user_id}).scalar()
        except:
            payments_count = 0
            print("   ⚠️ Таблица payments недоступна или имеет другую структуру")
        
        # Подсчитываем транскрипции и анализы
        transcriptions_count = db.execute(text("""
            SELECT COUNT(*) FROM transcriptions t 
            JOIN audio_files af ON t.file_id = af.file_id 
            WHERE af.user_id = :user_id
        """), {"user_id": user_id}).scalar()
        
        analyses_count = db.execute(text("""
            SELECT COUNT(*) FROM analyses a 
            JOIN transcriptions t ON a.transcription_id = t.transcription_id 
            JOIN audio_files af ON t.file_id = af.file_id 
            WHERE af.user_id = :user_id
        """), {"user_id": user_id}).scalar()
        
        print(f"\n📊 Связанные данные:")
        print(f"   Сессий: {sessions_count}")
        print(f"   Аудиофайлов: {audio_files_count}")
        print(f"   Транскрипций: {transcriptions_count}")
        print(f"   Анализов: {analyses_count}")
        print(f"   Платежей: {payments_count}")
        
        # Подтверждение удаления
        confirm = input(f"\n⚠️  ВНИМАНИЕ! Это действие нельзя отменить!\nВы уверены, что хотите удалить пользователя и ВСЕ его данные? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Удаление отменено")
            return
        
        print("\n🗑️  Начинаем удаление...")
        
        # Удаляем в правильном порядке через SQL
        
        # 1. Удаляем анализы
        if analyses_count > 0:
            deleted_analyses = db.execute(text("""
                DELETE a FROM analyses a 
                JOIN transcriptions t ON a.transcription_id = t.transcription_id 
                JOIN audio_files af ON t.file_id = af.file_id 
                WHERE af.user_id = :user_id
            """), {"user_id": user_id}).rowcount
            print(f"   ✅ Удалено анализов: {deleted_analyses}")
        
        # 2. Удаляем транскрипции
        if transcriptions_count > 0:
            deleted_transcriptions = db.execute(text("""
                DELETE t FROM transcriptions t 
                JOIN audio_files af ON t.file_id = af.file_id 
                WHERE af.user_id = :user_id
            """), {"user_id": user_id}).rowcount
            print(f"   ✅ Удалено транскрипций: {deleted_transcriptions}")
        
        # 3. Удаляем аудиофайлы
        if audio_files_count > 0:
            deleted_files = db.execute(text("DELETE FROM audio_files WHERE user_id = :user_id"), {"user_id": user_id}).rowcount
            print(f"   ✅ Удалено аудиофайлов: {deleted_files}")
        
        # 4. Удаляем платежи (если таблица существует)
        if payments_count > 0:
            try:
                deleted_payments = db.execute(text("DELETE FROM payments WHERE user_id = :user_id"), {"user_id": user_id}).rowcount
                print(f"   ✅ Удалено платежей: {deleted_payments}")
            except Exception as e:
                print(f"   ⚠️ Не удалось удалить платежи: {e}")
        
        # 5. Удаляем сессии
        if sessions_count > 0:
            deleted_sessions = db.execute(text("DELETE FROM sessions WHERE user_id = :user_id"), {"user_id": user_id}).rowcount
            print(f"   ✅ Удалено сессий: {deleted_sessions}")
        
        # 6. Удаляем самого пользователя
        deleted_user = db.execute(text("DELETE FROM users WHERE user_id = :user_id"), {"user_id": user_id}).rowcount
        print(f"   ✅ Удален пользователь: {deleted_user}")
        
        # Подтверждаем изменения
        db.commit()
        print(f"\n🎉 Пользователь {user_id} и все его данные успешно удалены!")
        
    except Exception as e:
        print(f"❌ Ошибка при удалении: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    user_id = "673770e6-97e8-4e3a-b5b1-90f2809372d4"
    delete_user_completely(user_id)
