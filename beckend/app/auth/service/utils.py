from app.auth.security import JWTUtils
from app.auth.schemas.auth import PayloadDTO,ExpireJwtDTO,JWTPayloadEN,TokenTypeEN, BlackLstMethod
from config import settings 
from jwt.exceptions import InvalidTokenError
from datetime import datetime,timedelta,timezone
from redis.asyncio import Redis
from typing import Literal
from app.exceptions import UserTokenError
from fastapi import Depends
import uuid, asyncio,time



#создаем отдлеьное expire  чтобы не вынести все данные оттуда  в класс
expire=ExpireJwtDTO(access_exp=settings.ACCESS_TOKEN_EXPIRE,
                    refresh_exp=settings.REFRESH_TOKEN_EXPIRE)





class JwtService:

    def __init__(self,utils: JWTUtils,
                 expire: ExpireJwtDTO,
                 r: Redis):
        self._jwt=utils
        self._redis=r
        self._expire=expire

        
    async def create_token(self,payload: PayloadDTO):
        if payload.token_type == TokenTypeEN.ACCESS:
            minute=self._expire.access_exp
        elif payload.token_type == TokenTypeEN.REFRESH:
            minute=self._expire.refresh_exp
        else: 
            raise InvalidTokenError
        expire_token=datetime.now(timezone.utc)+timedelta(minutes=minute)
        
        req={
            JWTPayloadEN.SUB: str(payload.user_id),
            JWTPayloadEN.NAME: payload.nik_name,
            JWTPayloadEN.EXP: expire_token,
            JWTPayloadEN.TYPE: payload.token_type,
            JWTPayloadEN.JTI: str(uuid.uuid4())
            }
        
        return await asyncio.to_thread(self._jwt.encode,req)

    
    async def _black_list_(self,payload, mode: Literal[BlackLstMethod.ADD,BlackLstMethod.GET]):
        
        if mode not in (BlackLstMethod.ADD, BlackLstMethod.GET):
            raise ValueError(f'Недопустимое значение {mode}. Ожидается `{BlackLstMethod.ADD}` or `{BlackLstMethod.GET}`!')
        
        key=f"black_list:{payload[JWTPayloadEN.JTI]}"
        
        if mode == BlackLstMethod.ADD:
            ttl=int(payload[JWTPayloadEN.EXP]-time.time())
            if ttl>0:
                await self._redis.set(key,1,ttl)

        else:
            
            return await self._redis.get(key)

            



    async def current_token(self,token: str):
        try:
            payload=await asyncio.to_thread(self._jwt.decode,token)

            if await self._black_list_(payload,mode=BlackLstMethod.GET):
                raise UserTokenError()
            
            if payload.get(JWTPayloadEN.TYPE)!=TokenTypeEN.ACCESS:
                raise InvalidTokenError()

            return {'id': uuid.UUID(payload[JWTPayloadEN.SUB]),
                    'type': payload[JWTPayloadEN.TYPE],
                    'nik_name': payload[JWTPayloadEN.NAME],
                    'jti': payload[JWTPayloadEN.JTI],
                    'exp': payload[JWTPayloadEN.EXP]}
                
        except:
            raise InvalidTokenError()


    
    async def logout(self,payload):
        await self._black_list_(payload=payload,mode=BlackLstMethod.ADD)
        if await self._black_list_(payload,mode=BlackLstMethod.GET):
            return True
        else:
            raise f'Не удалось выйти попробуйте еще раз!'
        