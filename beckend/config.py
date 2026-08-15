from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import (Field)

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




settings=Settings()