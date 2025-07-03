"""
API эндпоинты для получения вебхуков от Make.com
Новая архитектура: Make.com пишет в БД, а сюда присылает только уведомление.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transcription, Analysis, AudioFile
from app.schemas import TranscriptionWebhookData, AnalysisWebhookData
from app.models import ProcessingStatus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/transcription/completed")
async def transcription_completed(
    webhook_data: TranscriptionWebhookData,
    db: Session = Depends(get_db)
):
    """
    Вебхук от Make.com о завершении транскрибации.
    Make.com уже записал текст в БД. Мы только обновляем статус.
    """
    transcription = db.query(Transcription).filter(
        Transcription.file_id == webhook_data.file_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail=f"Транскрибация для file_id {webhook_data.file_id} не найдена")
    
    if webhook_data.status == "completed":
        transcription.status = ProcessingStatus.COMPLETED
        
        # Обновляем длительность файла для биллинга
        if webhook_data.duration_seconds is not None:
            audio_file = db.query(AudioFile).filter(AudioFile.file_id == webhook_data.file_id).first()
            if audio_file:
                audio_file.duration_seconds = webhook_data.duration_seconds
    else:
        transcription.status = ProcessingStatus.FAILED
        transcription.error_message = webhook_data.error_message or "Неизвестная ошибка от Make.com"
        
    db.commit()
    return {"success": True, "message": "Статус транскрибации обновлен"}

@router.post("/analysis/completed")
async def analysis_completed(
    webhook_data: AnalysisWebhookData,
    db: Session = Depends(get_db)
):
    """
    Вебхук от Make.com о завершении анализа.
    Make.com уже записал результат в БД. Мы только обновляем статус.
    """
    analysis = db.query(Analysis).filter(
        Analysis.analysis_id == webhook_data.analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Анализ с id {webhook_data.analysis_id} не найден")
    
    if webhook_data.status == "completed":
        analysis.status = ProcessingStatus.COMPLETED
    else:
        analysis.status = ProcessingStatus.FAILED
        analysis.error_message = webhook_data.error_message or "Неизвестная ошибка от Make.com"
        
    db.commit()
    return {"success": True, "message": "Статус анализа обновлен"}
