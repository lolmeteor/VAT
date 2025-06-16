"""
Сервис для отправки вебхуков в Make.com
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from app.config import settings
from app.models import AnalysisType

class MakeWebhookService:
    def __init__(self):
        self.transcription_webhook_url = settings.make_transcription_webhook_url
        self.analysis_webhooks = settings.make_analysis_webhooks
    
    async def send_transcription_webhook(self, file_id: str, s3_url: str, user_id: str) -> bool:
        """
        Отправляет вебхук для запуска транскрибации
        """
        payload = {
            "file_id": file_id,
            "s3_url": s3_url,
            "user_id": user_id,
            "action": "transcribe"
        }
        
        return await self._send_webhook(self.transcription_webhook_url, payload)
    
    async def send_analysis_webhook(self, analysis_type: AnalysisType, transcription_id: str, 
                                  transcription_s3_url: str, analysis_id: str) -> bool:
        """
        Отправляет вебхук для запуска конкретного типа анализа
        """
        webhook_url = self.analysis_webhooks.get(analysis_type.value)
        if not webhook_url:
            raise ValueError(f"Webhook URL не найден для типа анализа: {analysis_type.value}")
        
        payload = {
            "analysis_id": analysis_id,
            "transcription_id": transcription_id,
            "transcription_s3_url": transcription_s3_url,
            "analysis_type": analysis_type.value,
            "action": "analyze"
        }
        
        return await self._send_webhook(webhook_url, payload)
    
    async def _send_webhook(self, url: str, payload: Dict[str, Any]) -> bool:
        """
        Отправляет HTTP POST запрос на указанный webhook URL
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Make.com обычно возвращает 200 при успешном получении webhook
                if response.status_code == 200:
                    return True
                else:
                    print(f"Webhook failed with status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Ошибка отправки webhook: {str(e)}")
            return False
    
    def get_analysis_display_names(self) -> Dict[str, str]:
        """
        Возвращает человекочитаемые названия типов анализа для интерфейса
        """
        return {
            "kp": "КП",
            "first_meeting": "Первая встреча",
            "follow_up_meeting": "Повторная встреча", 
            "protocol": "Протокол",
            "speaker1_psycho": "Анализ Спикер 1 (психологический)",
            "speaker1_negative": "Анализ Спикер 1 (негативные факторы)",
            "speaker2_psycho": "Анализ Спикер 2 (психологический)",
            "speaker2_negative": "Анализ Спикер 2 (негативные факторы)",
            "speaker3_psycho": "Анализ Спикер 3 (психологический)",
            "speaker3_negative": "Анализ Спикер 3 (негативные факторы)",
            "speaker4_psycho": "Анализ Спикер 4 (психологический)",
            "speaker4_negative": "Анализ Спикер 4 (негативные факторы)"
        }
