from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import (Field)
from enum import Enum
from functools import cached_property

BASE_DIR=Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env",
                                      enable_decoding=True,
                                       env_ignore_empty=True,
                                        extra='ignore')

    POSTGRES_HOST : str ='localhost'
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_NAME : str
    POSTGRES_PORT : int

    REDIS_HOST : str
    REDIS_USER: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    RBROKER_HOST: str
    RBROKER_USER: str
    RBROKER_PORT: int
    RBROKER_PASSWORD: str

    

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"

    @property
    def REDISE_URL(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    @property
    def RABBIT_BROKER_URL(self):
        return f"amqp://{self.RBROKER_USER}:{self.RBROKER_PASSWORD}@{self.RBROKER_HOST}:{self.RBROKER_PORT}"


settings=Settings()




