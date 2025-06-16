"""
API эндпоинты для получения вебхуков от Make.com
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.services.s3 import S3Service
from app.models import Transcription, Analysis, User
from app.models import ProcessingStatus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

class TranscriptionWebhookData(BaseModel):
    file_id: str
    transcription_id: Optional[str] = None
    transcription_text: Optional[str] = None
    status: str  # "completed" или "failed"
    error_message: Optional[str] = None

class AnalysisWebhookData(BaseModel):
    analysis_id: str
    status: str  # "completed" или "failed"
    docx_content: Optional[str] = None  # Base64 encoded
    pdf_content: Optional[str] = None   # Base64 encoded
    error_message: Optional[str] = None

@router.post("/transcription/completed")
async def transcription_completed(
    webhook_data: TranscriptionWebhookData,
    db: Session = Depends(get_db)
):
    """
    Вебхук от Make.com о завершении транскрибации
    """
    # Находим транскрибацию по file_id
    transcription = db.query(Transcription).filter(
        Transcription.file_id == webhook_data.file_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")
    
    try:
        if webhook_data.status == "completed" and webhook_data.transcription_text:
            # Сохраняем текст транскрибации в S3
            s3_service = S3Service()
            s3_url = s3_service.upload_transcription(
                transcription_text=webhook_data.transcription_text,
                transcription_id=transcription.transcription_id
            )
            
            # Обновляем статус транскрибации
            transcription.s3_link_text = s3_url
            transcription.status = ProcessingStatus.COMPLETED
            
        else:
            # Транскрибация не удалась
            transcription.status = ProcessingStatus.FAILED
            transcription.error_message = webhook_data.error_message or "Ошибка транскрибации"
        
        db.commit()
        
        return {"success": True, "message": "Статус транскрибации обновлен"}
        
    except Exception as e:
        db.rollback()
        transcription.status = ProcessingStatus.FAILED
        transcription.error_message = f"Ошибка обработки результата: {str(e)}"
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/completed")
async def analysis_completed(
    webhook_data: AnalysisWebhookData,
    db: Session = Depends(get_db)
):
    """
    Вебхук от Make.com о завершении анализа
    """
    # Находим анализ по analysis_id
    analysis = db.query(Analysis).filter(
        Analysis.analysis_id == webhook_data.analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    
    try:
        if webhook_data.status == "completed":
            s3_service = S3Service()
            
            # Сохраняем DOCX документ, если есть
            if webhook_data.docx_content:
                import base64
                docx_bytes = base64.b64decode(webhook_data.docx_content)
                docx_url = s3_service.upload_analysis_document(
                    document_content=docx_bytes,
                    analysis_id=analysis.analysis_id,
                    file_type="docx"
                )
                analysis.s3_docx_link = docx_url
            
            # Сохраняем PDF документ, если есть
            if webhook_data.pdf_content:
                import base64
                pdf_bytes = base64.b64decode(webhook_data.pdf_content)
                pdf_url = s3_service.upload_analysis_document(
                    document_content=pdf_bytes,
                    analysis_id=analysis.analysis_id,
                    file_type="pdf"
                )
                analysis.s3_pdf_link = pdf_url
            
            analysis.status = ProcessingStatus.COMPLETED
            
        else:
            # Анализ не удался
            analysis.status = ProcessingStatus.FAILED
            analysis.error_message = webhook_data.error_message or "Ошибка анализа"
        
        db.commit()
        
        return {"success": True, "message": "Статус анализа обновлен"}
        
    except Exception as e:
        db.rollback()
        analysis.status = ProcessingStatus.FAILED
        analysis.error_message = f"Ошибка обработки результата: {str(e)}"
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))
