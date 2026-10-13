from app.auth.schemas.settings import SettingsAuthDTO
from app.auth.schemas.auth  import ExpireJwtDTO
from config import settings


jwt_conf=SettingsAuthDTO(
        private_key=settings.SECRET_KEY,
        public_key=settings.PUBLIC_KEY,
        algorithm=settings.ALGORITHM,
        access_exp=settings.ACCESS_TOKEN_EXPIRE,
        refresh_exp=settings.REFRESH_TOKEN_EXPIRE,
        two_factory=settings.TWO_FACTORY_EXPIRE)


expire=ExpireJwtDTO(access_exp=settings.ACCESS_TOKEN_EXPIRE,
                    refresh_exp=settings.REFRESH_TOKEN_EXPIRE)


secret_totp=settings.ENCRYPT_SECRET_KEY