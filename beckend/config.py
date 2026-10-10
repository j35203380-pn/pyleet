from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import (Field,SecretStr)
from enum import Enum
from functools import cached_property
from cryptography.hazmat.primitives import serialization
from urllib.parse import quote


BASE_DIR=Path(__file__).parent.parent


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env",
                                      enable_decoding=True,
                                       env_ignore_empty=True,
                                        extra='ignore')

    POSTGRES_HOST : str ='localhost'
    POSTGRES_USER : SecretStr
    POSTGRES_PASSWORD : SecretStr
    POSTGRES_NAME : SecretStr
    POSTGRES_PORT : int

    REDIS_HOST : SecretStr
    REDIS_USER: SecretStr
    REDIS_PORT: int
    REDIS_PASSWORD: SecretStr

    RBROKER_HOST: SecretStr
    RBROKER_USER: SecretStr
    RBROKER_PORT: int
    RBROKER_PASSWORD: SecretStr

    secret_key_path : SecretStr
    public_key_path : SecretStr
    ALGORITHM : str
    SECRET_KEY_PARAPHRASE: SecretStr
    ACCESS_TOKEN_EXPIRE: int =60*60
    REFRESH_TOKEN_EXPIRE: int=60*60*24*30
    
    @cached_property
    def SECRET_KEY(self):
        file_path=BASE_DIR / self.secret_key_path.get_secret_value()
        file=file_path.read_bytes()
        paraphase=self.SECRET_KEY_PARAPHRASE.get_secret_value().encode()
        return serialization.load_pem_private_key(data=file,password=None)

    @cached_property
    def PUBLIC_KEY(self):
        file_path=BASE_DIR / self.public_key_path.get_secret_value()
        return file_path.read_bytes()

    @property
    def DATABASE_URL(self):
        user=quote(self.POSTGRES_USER.get_secret_value(), safe="")
        pwd=quote(self.POSTGRES_PASSWORD.get_secret_value(), safe="")
        return f"postgresql+asyncpg://{user}:{pwd}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME.get_secret_value()}"

    @property
    def REDISE_URL(self):
        return f'redis://{self.REDIS_HOST.get_secret_value()}:{self.REDIS_PORT}'

    @property
    def RABBIT_BROKER_URL(self):
        user=quote(self.RBROKER_USER.get_secret_value(), safe="")
        pwd=quote(self.RBROKER_PASSWORD.get_secret_value(), safe="")
        return f"amqp://{user}:{pwd}@{self.RBROKER_HOST.get_secret_value()}:{self.RBROKER_PORT}"


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