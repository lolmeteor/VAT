"""
API эндпоинты для работы с аудиофайлами
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Response
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database import get_db
from app.services.auth import AuthService
from app.services.s3 import S3Service
from app.services.make_webhook import MakeWebhookService
from app.services.document_generator import DocumentGeneratorService
from app.models import User, AudioFile, Transcription
from app.schemas import AudioFileResponse, ApiResponse, UserResponse, TranscriptionResponse
from app.models import AudioFileStatus, ProcessingStatus

router = APIRouter(prefix="/files", tags=["files"])

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

@router.post("/upload", response_model=AudioFileResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Загрузка аудиофайла
    """
    # Проверяем тип файла
    allowed_extensions = ['mp3', 'wav', 'm4a', 'flac', 'ogg']
    file_extension = file.filename.split('.')[-1].lower() if file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Проверяем размер файла (1 ГБ = 1073741824 байт)
    file_content = await file.read()
    if len(file_content) > 1073741824:
        raise HTTPException(status_code=400, detail="Размер файла превышает 1 ГБ")
    
    try:
        # Загружаем файл в S3
        s3_service = S3Service()
        file_id, s3_url = s3_service.upload_audio_file(
            file_content=file_content,
            original_filename=file.filename,
            user_id=current_user.user_id
        )
        
        # Сохраняем информацию о файле в БД
        audio_file = AudioFile(
            file_id=file_id,
            user_id=current_user.user_id,
            original_file_name=file.filename,
            s3_link=s3_url,
            file_size_bytes=len(file_content),
            status=AudioFileStatus.uploaded  # ИСПРАВЛЕНО: используем lowercase
        )
        
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        
        # Создаем запись транскрибации
        transcription = Transcription(
            transcription_id=str(uuid.uuid4()),
            file_id=file_id,
            status=ProcessingStatus.pending
        )
        
        db.add(transcription)
        db.commit()
        
        # Отправляем вебхук в Make.com для транскрибации
        webhook_service = MakeWebhookService()
        webhook_sent = await webhook_service.send_transcription_webhook(
            file_id=file_id,
            s3_url=s3_url,
            user_id=current_user.user_id
        )
        
        if webhook_sent:
            transcription.status = ProcessingStatus.processing
            db.commit()
        
        return AudioFileResponse.from_orm(audio_file)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

@router.get("/", response_model=List[AudioFileResponse])
async def get_user_files(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение списка файлов пользователя
    """
    files = db.query(AudioFile).filter(
        AudioFile.user_id == current_user.user_id
    ).order_by(AudioFile.created_at.desc()).all()
    
    return [AudioFileResponse.from_orm(file) for file in files]

@router.get("/{file_id}", response_model=AudioFileResponse)
async def get_file_info(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение информации о конкретном файле
    """
    audio_file = db.query(AudioFile).filter(
        AudioFile.file_id == file_id,
        AudioFile.user_id == current_user.user_id
    ).first()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return AudioFileResponse.from_orm(audio_file)

# ДОБАВЛЯЕМ недостающий эндпоинт для получения transcription по file_id
@router.get("/{file_id}/transcription", response_model=TranscriptionResponse)
async def get_transcription_by_file_id(
    file_id: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Получение транскрипции по file_id
    """
    # Проверяем что файл принадлежит пользователю
    audio_file = db.query(AudioFile).filter(
        AudioFile.file_id == file_id,
        AudioFile.user_id == current_user.user_id
    ).first()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Получаем транскрипцию для этого файла
    transcription = db.query(Transcription).filter(
        Transcription.file_id == file_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    return TranscriptionResponse.from_orm(transcription)

@router.get("/{file_id}/transcription/download/{doc_format}")
async def download_transcription(
    file_id: str,
    doc_format: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Генерация и скачивание документа с транскрипцией.
    """
    if doc_format not in ["txt", "docx"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат. Доступны: txt, docx")

    transcription = db.query(Transcription).join(AudioFile).filter(
        AudioFile.file_id == file_id,
        AudioFile.user_id == current_user.user_id
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Транскрипция не найдена или у вас нет доступа.")
    
    if transcription.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Транскрипция еще не завершена.")

    doc_service = DocumentGeneratorService()
    
    if doc_format == "txt":
        content = doc_service.generate_transcription_txt(transcription)
        media_type = "text/plain"
        filename = f"transcription_{file_id}.txt"
    else: # docx
        content = doc_service.generate_transcription_docx(transcription)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"transcription_{file_id}.docx"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
