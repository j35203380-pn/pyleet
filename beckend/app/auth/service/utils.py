from app.auth.security import JWTUtils
from app.auth.schemas.auth import (PayloadDTO,PayloadSetEN,TokenTypeEN, 
                                   BlackLstMethod,PayloadGetEN)
from jwt.exceptions import InvalidTokenError
from datetime import datetime,timedelta,timezone
from typing import Literal
from app.exceptions import UserTokenError
from app.auth.settings.base import SettingsAuthDTO
from app.auth.ports.cache import Cache
import uuid, asyncio,time








class JwtService:

    def __init__(self,utils: JWTUtils,
                 settings: SettingsAuthDTO,
                 r: Cache):
        self._jwt=utils
        self._redis=r
        self._settings=settings

        
    async def create_token(self,payload: PayloadDTO):
        if payload.token_type == TokenTypeEN.ACCESS:
            second=self._settings.access_exp
        elif payload.token_type == TokenTypeEN.REFRESH:
            second=self._settings.refresh_exp
        else: 
            raise InvalidTokenError
        expire_token=datetime.now(timezone.utc)+timedelta(seconds=second)
        
        req={
            PayloadSetEN.SUB: str(payload.user_id),
            PayloadSetEN.NAME: payload.nik_name,
            PayloadSetEN.EXP: expire_token,
            PayloadSetEN.TYPE: payload.token_type,
            PayloadSetEN.JTI: str(uuid.uuid4())
            }
        
        return await asyncio.to_thread(
                            self._jwt.encode,req,
                            self._settings.private_key,
                            self._settings.algorithm)

    
    async def _black_list_(self,payload, mode: Literal[BlackLstMethod.ADD,BlackLstMethod.GET]):
        
        if mode not in (BlackLstMethod.ADD, BlackLstMethod.GET):
            raise ValueError(f'Недопустимое значение {mode}. Ожидается `{BlackLstMethod.ADD}` or `{BlackLstMethod.GET}`!')
        
        key=f"black_list:{payload[PayloadSetEN.JTI]}"
        
        if mode == BlackLstMethod.ADD:
            ttl=int(payload[PayloadSetEN.EXP]-time.time())
            if ttl>0:
                await self._redis.set(key,1,ttl)

        else:
            
            return await self._redis.get(key)

            



    async def current_token(self,token: str):
        try:
            payload=await asyncio.to_thread(
                                self._jwt.decode,token,
                                self._settings.public_key,
                                self._settings.algorithm)

            if await self._black_list_(payload,mode=BlackLstMethod.GET):
                raise UserTokenError()
            
            if payload.get(PayloadSetEN.TYPE)!=TokenTypeEN.ACCESS:
                raise InvalidTokenError()

            return {PayloadGetEN.ID: uuid.UUID(payload[PayloadSetEN.SUB]),
                    PayloadGetEN.TYPE: payload[PayloadSetEN.TYPE],
                    PayloadGetEN.NIK_NAME: payload[PayloadSetEN.NAME],
                    PayloadGetEN.JTI: payload[PayloadSetEN.JTI],
                    PayloadGetEN.EXP: payload[PayloadSetEN.EXP]}
                
        except:
            raise InvalidTokenError()


    
    async def logout(self,payload):
        await self._black_list_(payload=payload,mode=BlackLstMethod.ADD)
        if await self._black_list_(payload,mode=BlackLstMethod.GET):
            return f'Вы успешно вышли'
        else:
            raise f'Не удалось выйти попробуйте еще раз!'
        