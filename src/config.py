from typing import Any
from dotenv import load_dotenv

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment

load_dotenv()

class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(CustomBaseSettings):
    POSTGRES_URL: PostgresDsn
    ENVIRONMENT: Environment = Environment.PRODUCTION
    REDIS_HOST: str
    REDIS_PORT: int
    APP_VERSION: str = "0.1"


settings = Config() # type: ignore


class LogConfig(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "console": {
            "format": '%(asctime)s %(levelname)s %(module)s %(message)s',
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
        "file": {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s',
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
    }
    handlers: dict = {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'console',
        },
       'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './logs/backend.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'file',
        },
    }
    loggers: dict = {
        'root': {
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'auth': {
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'payment': {
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'admin': {
            'handlers': ['file', 'console'],
            'propagate': False,
        }
    }


app_configs: dict[str, Any] = {"title": "Smart-Process"}
if settings.ENVIRONMENT.is_deploy:
    app_configs["root_path"] = f"{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None