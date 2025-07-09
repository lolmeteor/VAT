"""
API эндпоинты для работы с анализами
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database import get_db
from app.services.auth import AuthService
from app.services.make_webhook import MakeWebhookService
from app.models import Transcription, Analysis, AudioFile
from app.schemas import AnalysisResponse, AnalysisRequest, ApiResponse, UserResponse
from app.models import ProcessingStatus, AnalysisType
from app.services.document_generator import DocumentGeneratorService

router = APIRouter(prefix="/analyses", tags=["analyses"])

async def get_current_user_dependency(request: Request, db: Session = Depends(get_db)) -> UserResponse:
    """
    Dependency для получения текущего пользователя
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_session(session_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Сессия недействительна")
    
    return user

@router.post("/start", response_model=List[AnalysisResponse])
async def start_analyses(
    request_data: AnalysisRequest,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Запуск анализов для транскрибации
    """
    # Проверяем, что транскрибация существует и принадлежит пользователю
    transcription = db.query(Transcription).join(AudioFile).filter(
        Transcription.transcription_id == request_data.transcription_id,
        AudioFile.user_id == current_user.user_id,
        Transcription.status == ProcessingStatus.completed  # ИСПРАВЛЕНО: lowercase
    ).first()
    
    if not transcription:
        raise HTTPException(
            status_code=404, 
            detail="Транскрибация не найдена или еще не завершена"
        )
    
    if not transcription.s3_link_text:
        raise HTTPException(
            status_code=400,
            detail="Текст транскрибации недоступен"
        )
    
    created_analyses = []
    webhook_service = MakeWebhookService()
    
    for analysis_type in request_data.analysis_types:
        # Проверяем, не существует ли уже такой анализ
        existing_analysis = db.query(Analysis).filter(
            Analysis.transcription_id == request_data.transcription_id,
            Analysis.analysis_type == analysis_type
        ).first()
        
        if existing_analysis:
            created_analyses.append(AnalysisResponse.from_orm(existing_analysis))
            continue
        
        # Создаем новый анализ
        analysis = Analysis(
            analysis_id=str(uuid.uuid4()),
            transcription_id=request_data.transcription_id,
            analysis_type=analysis_type,
            status=ProcessingStatus.pending  # ИСПРАВЛЕНО: lowercase
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Отправляем вебхук в Make.com
        try:
            webhook_sent = await webhook_service.send_analysis_webhook(
                analysis_type=analysis_type,
                transcription_id=request_data.transcription_id,
                transcription_s3_url=transcription.s3_link_text,
                analysis_id=analysis.analysis_id
            )
            
            if webhook_sent:
                analysis.status = ProcessingStatus.processing  # ИСПРАВЛЕНО: lowercase
                db.commit()
            
            created_analyses.append(AnalysisResponse.from_orm(analysis))
            
        except Exception as e:
            analysis.status = ProcessingStatus.failed  # ИСПРАВЛЕНО: lowercase
            analysis.error_message = f"Ошибка отправки вебхука: {str(e)}"
            db.commit()
            created_analyses.append(AnalysisResponse.from_orm(analysis))
    
    return created_analyses

@router.get("/transcription/{transcription_id}", response_model=List[AnalysisResponse])
async def get_analyses_for_transcription(
    transcription_id: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение всех анализов для транскрибации
    """
    # Проверяем доступ к транскрибации
    transcription = db.query(Transcription).join(AudioFile).filter(
        Transcription.transcription_id == transcription_id,
        AudioFile.user_id == current_user.user_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")
    
    # Получаем ВСЕ анализы для транскрипции
    analyses = db.query(Analysis).filter(
        Analysis.transcription_id == transcription_id
    ).order_by(Analysis.created_at.desc()).all()
    
    return [AnalysisResponse.from_orm(analysis) for analysis in analyses]

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение информации о конкретном анализе
    """
    analysis = db.query(Analysis).join(Transcription).join(AudioFile).filter(
        Analysis.analysis_id == analysis_id,
        AudioFile.user_id == current_user.user_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    
    return AnalysisResponse.from_orm(analysis)

@router.get("/types/available")
async def get_available_analysis_types():
    """
    Получение списка доступных типов анализа с их названиями
    """
    webhook_service = MakeWebhookService()
    display_names = webhook_service.get_analysis_display_names()
    
    return {
        "success": True,
        "data": {
            "types": [
                {
                    "id": analysis_type.value,
                    "name": display_names.get(analysis_type.value, analysis_type.value),
                    "description": f"Проведение анализа: {display_names.get(analysis_type.value, analysis_type.value)}"
                }
                for analysis_type in AnalysisType
            ]
        }
    }

@router.get("/{analysis_id}/download/{doc_format}")
async def download_analysis(
    analysis_id: str,
    doc_format: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Генерация и скачивание документа с анализом.
    """
    if doc_format not in ["docx", "pdf"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат. Доступны: docx, pdf")

    analysis = db.query(Analysis).join(Transcription).join(AudioFile).filter(
        Analysis.analysis_id == analysis_id,
        AudioFile.user_id == current_user.user_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Анализ не найден или у вас нет доступа.")

    if analysis.status != ProcessingStatus.completed:  # ИСПРАВЛЕНО: lowercase
        raise HTTPException(status_code=400, detail="Анализ еще не завершен.")

    doc_service = DocumentGeneratorService()

    if doc_format == "docx":
        content = doc_service.generate_analysis_docx(analysis)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"analysis_{analysis.analysis_type.value}_{analysis_id}.docx"
    else: # pdf - пока не реализовано, но эндпоинт есть
        raise HTTPException(status_code=501, detail="Генерация PDF пока не реализована.")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
