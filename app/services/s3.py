"""
Сервис для работы с S3-совместимым хранилищем
"""
import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region
        )
        self.bucket_name = settings.s3_bucket_name

    async def upload_file(self, file_content: bytes, file_key: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """
        Загружает файл в S3 и возвращает URL
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            # Формируем URL файла
            file_url = f"{settings.s3_endpoint_url}/{self.bucket_name}/{file_key}"
            logger.info(f"Файл успешно загружен: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"Ошибка загрузки файла в S3: {e}")
            return None

    async def delete_file(self, file_key: str) -> bool:
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

    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
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

# Глобальный экземпляр сервиса
s3_service = S3Service()
