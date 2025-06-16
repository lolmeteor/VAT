"""
Сервис для работы с S3 хранилищем Reg.ru
"""
import boto3
import uuid
from typing import Optional
from botocore.exceptions import ClientError
from app.config import settings

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region
        )
        self.bucket_name = settings.s3_bucket_name
    
    def upload_audio_file(self, file_content: bytes, original_filename: str, user_id: str) -> tuple[str, str]:
        """
        Загружает аудиофайл в S3 и возвращает (file_id, s3_url)
        """
        file_id = str(uuid.uuid4())
        file_extension = original_filename.split('.')[-1].lower()
        
        # Создаем структурированный путь: audio/user_id/year/month/file_id.ext
        from datetime import datetime
        now = datetime.utcnow()
        s3_key = f"audio/{user_id}/{now.year}/{now.month:02d}/{file_id}.{file_extension}"
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=self._get_content_type(file_extension)
            )
            
            s3_url = f"{settings.s3_endpoint_url}/{self.bucket_name}/{s3_key}"
            return file_id, s3_url
            
        except ClientError as e:
            raise Exception(f"Ошибка загрузки файла в S3: {str(e)}")
    
    def upload_transcription(self, transcription_text: str, transcription_id: str) -> str:
        """
        Загружает текст транскрипции в S3
        """
        from datetime import datetime
        now = datetime.utcnow()
        s3_key = f"transcriptions/{now.year}/{now.month:02d}/{transcription_id}.txt"
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=transcription_text.encode('utf-8'),
                ContentType='text/plain; charset=utf-8'
            )
            
            return f"{settings.s3_endpoint_url}/{self.bucket_name}/{s3_key}"
            
        except ClientError as e:
            raise Exception(f"Ошибка загрузки транскрипции в S3: {str(e)}")
    
    def upload_analysis_document(self, document_content: bytes, analysis_id: str, file_type: str) -> str:
        """
        Загружает документ анализа (.docx или .pdf) в S3
        """
        from datetime import datetime
        now = datetime.utcnow()
        s3_key = f"analyses/{now.year}/{now.month:02d}/{analysis_id}.{file_type}"
        
        try:
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if file_type == 'docx' else 'application/pdf'
            
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=document_content,
                ContentType=content_type
            )
            
            return f"{settings.s3_endpoint_url}/{self.bucket_name}/{s3_key}"
            
        except ClientError as e:
            raise Exception(f"Ошибка загрузки документа анализа в S3: {str(e)}")
    
    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Генерирует временную ссылку для скачивания файла
        """
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
        except ClientError as e:
            raise Exception(f"Ошибка генерации ссылки для скачивания: {str(e)}")
    
    def delete_file(self, s3_url: str) -> bool:
        """
        Удаляет файл из S3
        """
        try:
            # Извлекаем ключ из URL
            s3_key = s3_url.replace(f"{settings.s3_endpoint_url}/{self.bucket_name}/", "")
            
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
            
        except ClientError as e:
            print(f"Ошибка удаления файла из S3: {str(e)}")
            return False
    
    def _get_content_type(self, file_extension: str) -> str:
        """
        Определяет MIME тип по расширению файла
        """
        content_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'flac': 'audio/flac',
            'ogg': 'audio/ogg'
        }
        return content_types.get(file_extension.lower(), 'audio/mpeg')
