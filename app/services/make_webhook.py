"""
Сервис для отправки webhook'ов в Make.com
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings
from app.models import AnalysisType

logger = logging.getLogger(__name__)

class MakeWebhookService:
    def __init__(self):
        self.transcription_webhook_url = settings.make_transcription_webhook_url
        self.analysis_webhooks = settings.make_analysis_webhooks
        self.timeout = 30.0

    async def send_transcription_webhook(self, file_id: str, s3_url: str, user_id: str) -> bool:
        """
        Отправляет webhook для запуска транскрибации в Make.com
        """
        if not self.transcription_webhook_url:
            logger.warning("Make transcription webhook URL не настроен")
            return False

        data = {
            "event_type": "transcription_start",
            "file_id": file_id,
            "s3_url": s3_url,
            "user_id": user_id
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.transcription_webhook_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Transcription webhook успешно отправлен для file_id: {file_id}")
                    return True
                else:
                    logger.error(f"Ошибка отправки transcription webhook: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Таймаут при отправке transcription webhook в Make.com")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке transcription webhook: {e}")
            return False

    async def send_analysis_webhook(self, analysis_type: AnalysisType, transcription_id: str, 
                                  transcription_s3_url: str, analysis_id: str) -> bool:
        """
        Отправляет webhook для запуска анализа в Make.com
        """
        webhook_url = self.analysis_webhooks.get(analysis_type.value)
        
        if not webhook_url:
            logger.warning(f"Webhook URL для анализа {analysis_type.value} не настроен")
            return False

        data = {
            "event_type": "analysis_start",
            "analysis_id": analysis_id,
            "analysis_type": analysis_type.value,
            "transcription_id": transcription_id,
            "transcription_s3_url": transcription_s3_url
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Analysis webhook успешно отправлен для {analysis_type.value}, analysis_id: {analysis_id}")
                    return True
                else:
                    logger.error(f"Ошибка отправки analysis webhook для {analysis_type.value}: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Таймаут при отправке analysis webhook для {analysis_type.value}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке analysis webhook для {analysis_type.value}: {e}")
            return False

    def get_analysis_display_names(self) -> Dict[str, str]:
        """
        Возвращает человекочитаемые названия типов анализа
        """
        return {
            "kp": "Ключевые пункты",
            "first_meeting": "Анализ первой встречи",
            "follow_up_meeting": "Анализ повторной встречи", 
            "protocol": "Протокол встречи",
            "speaker1_psycho": "Психологический портрет спикера 1",
            "speaker1_negative": "Негативные моменты спикера 1",
            "speaker2_psycho": "Психологический портрет спикера 2",
            "speaker2_negative": "Негативные моменты спикера 2",
            "speaker3_psycho": "Психологический портрет спикера 3",
            "speaker3_negative": "Негативные моменты спикера 3",
            "speaker4_psycho": "Психологический портрет спикера 4",
            "speaker4_negative": "Негативные моменты спикера 4"
        }
