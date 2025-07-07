"""
Сервис для работы с S3-совместимым хранилищем
"""
import boto3
from botocore.exceptions import ClientError
import logging
import uuid
from typing import Optional, Tuple
from app.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,  # ИСПРАВЛЕНО
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region
        )
        self.bucket_name = settings.s3_bucket_name

    def upload_audio_file(self, file_content: bytes, original_filename: str, user_id: str) -> Tuple[str, str]:
        """
        Загружает аудиофайл в S3 и возвращает file_id и URL
        """
        try:
            # Генерируем уникальный file_id
            file_id = str(uuid.uuid4())
            
            # Определяем расширение файла
            file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else 'mp3'
            
            # Формируем ключ файла в S3
            file_key = f"audio/{user_id}/{file_id}.{file_extension}"
            
            # Определяем content type
            content_type_map = {
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'm4a': 'audio/mp4',
                'flac': 'audio/flac',
                'ogg': 'audio/ogg'
            }
            content_type = content_type_map.get(file_extension, 'audio/mpeg')
            
            # Загружаем файл
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'original_filename': original_filename,
                    'user_id': user_id,
                    'file_id': file_id
                }
            )
            
            # Формируем URL файла
            file_url = f"{settings.s3_endpoint_url}/{self.bucket_name}/{file_key}"
            logger.info(f"Аудиофайл успешно загружен: {file_url}")
            
            return file_id, file_url
            
        except ClientError as e:
            logger.error(f"Ошибка загрузки аудиофайла в S3: {e}")
            raise Exception(f"Ошибка загрузки файла: {str(e)}")

    def upload_text_file(self, text_content: str, file_key: str) -> Optional[str]:
        """
        Загружает текстовый файл в S3
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=text_content.encode('utf-8'),
                ContentType='text/plain; charset=utf-8'
            )
            
            file_url = f"{settings.s3_endpoint_url}/{self.bucket_name}/{file_key}"
            logger.info(f"Текстовый файл успешно загружен: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"Ошибка загрузки текстового файла в S3: {e}")
            return None

    def upload_document(self, document_content: bytes, file_key: str, content_type: str) -> Optional[str]:
        """
        Загружает документ (DOCX, PDF) в S3
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=document_content,
                ContentType=content_type
            )
            
            file_url = f"{settings.s3_endpoint_url}/{self.bucket_name}/{file_key}"
            logger.info(f"Документ успешно загружен: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"Ошибка загрузки документа в S3: {e}")
            return None

    def delete_file(self, file_key: str) -> bool:
        """
        Удаляет файл из S3
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Файл успешно удален: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Ошибка удаления файла из S3: {e}")
            return False

    def get_presigned_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Генерирует подписанный URL для доступа к файлу
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expires_in
            )
            return url
            
        except ClientError as e:
            logger.error(f"Ошибка генерации URL для файла: {e}")
            return None
