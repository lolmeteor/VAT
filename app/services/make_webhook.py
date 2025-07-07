"""
Сервис для отправки webhook'ов в Make.com
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class MakeWebhookService:
    def __init__(self):
        self.webhook_url = settings.make_webhook_url
        self.timeout = 30.0

    async def send_webhook(self, data: Dict[str, Any]) -> bool:
        """
        Отправляет данные в Make.com webhook
        """
        if not self.webhook_url:
            logger.warning("Make webhook URL не настроен")
            return False

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Webhook успешно отправлен в Make.com: {data.get('event_type', 'unknown')}")
                    return True
                else:
                    logger.error(f"Ошибка отправки webhook в Make.com: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Таймаут при отправке webhook в Make.com")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке webhook в Make.com: {e}")
            return False

    async def send_analysis_started(self, file_id: str, analysis_types: list, user_id: str) -> bool:
        """
        Отправляет уведомление о начале анализа
        """
        data = {
            "event_type": "analysis_started",
            "file_id": file_id,
            "user_id": user_id,
            "analysis_types": analysis_types,
            "timestamp": "2025-01-16T12:00:00Z"
        }
        return await self.send_webhook(data)

    async def send_analysis_completed(self, file_id: str, analysis_id: str, analysis_type: str, result_urls: Dict[str, str]) -> bool:
        """
        Отправляет уведомление о завершении анализа
        """
        data = {
            "event_type": "analysis_completed",
            "file_id": file_id,
            "analysis_id": analysis_id,
            "analysis_type": analysis_type,
            "result_urls": result_urls,
            "timestamp": "2025-01-16T12:00:00Z"
        }
        return await self.send_webhook(data)

    async def send_transcription_completed(self, file_id: str, transcription_id: str, transcription_url: str) -> bool:
        """
        Отправляет уведомление о завершении транскрипции
        """
        data = {
            "event_type": "transcription_completed",
            "file_id": file_id,
            "transcription_id": transcription_id,
            "transcription_url": transcription_url,
            "timestamp": "2025-01-16T12:00:00Z"
        }
        return await self.send_webhook(data)

# Глобальный экземпляр сервиса
make_webhook_service = MakeWebhookService()
