from app.auth.security import CryptoAuth
from app.auth.repositories.repositories import AuthRepositories
from app.auth.schemas.schemas import UserAuthAdd
from app.auth.schemas.auth import PayloadDTO,TokenTypeEN
from sqlalchemy.exc import IntegrityError
from app.exceptions import UserNotFound
from app.auth.service.utils import JwtService
import asyncio, logging




class UserAuthService:
    def __init__(self,repo: AuthRepositories, jwt_: JwtService):
        self._db=repo
        self._jwt=jwt_
    
    async def add_user(self,users: UserAuthAdd):
        logging.info('запрос принят')
        password_hash=await asyncio.to_thread(CryptoAuth.hash_password,users.password)
        us=dict(
            name=users.name,nik_name=users.nik_name,
            email=users.email,password=password_hash
            )
        try:
            await self._db.user_add(us)
            return {"statuse": "200 OK"}
        except IntegrityError:
            raise UserNotFound()

    async def get_user(self,username: str, password: str):
        
        user=await self._db.user_login(username=username)
        if not user:
            raise UserNotFound()
        id,nik_name,hash_password=user.id, user.nik_name, user.password
        veryf_password=await asyncio.to_thread(CryptoAuth.verify_password,hash_password,password)
        if not veryf_password:
            raise UserNotFound()

        token= self._jwt.create_token(PayloadDTO(user_id=id,token_type=TokenTypeEN.ACCESS,nik_name=nik_name))
        token_refresh= self._jwt.create_token(PayloadDTO(user_id=id,token_type=TokenTypeEN.REFRESH,nik_name=nik_name))
        t=await asyncio.gather(token,token_refresh)
        return t[0]




