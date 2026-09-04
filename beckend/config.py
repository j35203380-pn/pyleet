from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import (Field)
from enum import Enum


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

    secret_key_path : str = Field(validation_alias='JWT_SECRET_KEY')
    public_key_path : str = Field(validation_alias="JWT_PUBLIC_KEY")
    ALGORITHM : str

    
    @property
    def SECRET_KEY(self):
        file_path=BASE_DIR / self.secret_key_path
        return file_path.read_text()

    @property
    def PUBLIC_KEY(self) -> str:
        file_path=BASE_DIR / self.public_key_path
        return file_path.read_text()

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


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"        
    WRONG_ANSWER = "wrong_answer" 
    RUNTIME_ERROR = "runtime_error"  
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded" 


class DifficultyLevel(str,Enum):
    EASY='EASY'
    MEDIUM='MEDIUM'
    HARD='HARD'