"""
Конфигурация приложения VAT (Voice Analysis Tool)
Продакшн настройки с HTTPS
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Основные настройки приложения
    app_env: str = "production"
    app_secret_key: str
    app_base_url: str = "https://www.vertexassistant.ru"
    cors_allowed_origins: str = "https://www.vertexassistant.ru,https://www.vertexassistant.ru:443,https://vertexassistant.ru"
    
    # База данных MySQL - ВАШИ РЕАЛЬНЫЕ ДАННЫЕ
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "vat_db"
    db_user: str = "transcr"
    db_password: str = "transcr123"
    
    # Telegram
    telegram_bot_token: str
    telegram_login_widget_bot_name: str = "VertexAIassistantBOT"
    
    # S3 хранилище Reg.ru - ОБНОВЛЕННЫЕ ДАННЫЕ
    s3_endpoint_url: str = "https://s3.regru.cloud"
    s3_access_key_id: str = "8TVU2GJ3DLFZVS5MUI3L"
    s3_secret_access_key: str = "1ARu78H9fvqqDmDpDLJFVkVt0U5RQ1v8qlNdhpgb"
    s3_bucket_name: str = "vatbucket"
    s3_region: str = "ru-central1"
    
    # Make.com вебхуки
    make_transcription_webhook_url: str = "https://hook.eu2.make.com/4i2h74esxc38zqlxz6oexklp1ux1eacq"
    
    # Вебхуки для анализов
    make_analysis_webhooks: dict = {
        "kp": "https://hook.eu2.make.com/58ezljut6m4qmhohni26xm2toii696jr",
        "first_meeting": "https://hook.eu2.make.com/ui6aobd4krptmbmj5vhc6ckzahd2q12n",
        "follow_up_meeting": "https://hook.eu2.make.com/nyis0xninjeum0zkalwhox5xzw9t6d2r",
        "protocol": "https://hook.eu2.make.com/6vmqf4skjnd5nbsg1d8fetqtmoc15szm",
        "speaker1_psycho": "https://hook.eu2.make.com/w5dv1fwrfmb948dqempwu8bn97d9044j",
        "speaker1_negative": "https://hook.eu2.make.com/grumlwktfx2aig668vyz547r7z1ud7ge",
        "speaker2_psycho": "https://hook.eu2.make.com/wnpt8j5vgf2225xhio8jkszixsvp8kc0",
        "speaker2_negative": "https://hook.eu2.make.com/f59lysvck9kr40pmfc7ubc5vp1ymi9w2",
        "speaker3_psycho": "https://hook.eu2.make.com/8ekteipmngw3iiraz8s6i1425xsypcb3",
        "speaker3_negative": "https://hook.eu2.make.com/o3w3xeslh354qu1e2zmg8ropp7jxtkle",
        "speaker4_psycho": "https://hook.eu2.make.com/4auucokt7m3at0bk1qpzta0sx3din5h2",
        "speaker4_negative": "https://hook.eu2.make.com/5fvxpwvl0enl9ckbblinpvffcuck82y4"
    }
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
