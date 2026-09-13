from argon2 import PasswordHasher
from config import settings
import jwt
from datetime import timedelta,timezone,datetime
from fastapi  import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
import uuid
from argon2.exceptions import VerifyMismatchError
from app.redis_client import RedisConnect
from redis.asyncio import Redis
from typing import Annotated
import logging
import asyncio


redis=Annotated[Redis,Depends(RedisConnect)]

_semaphore=asyncio.Semaphore(20)


ph=PasswordHasher()

oauth_shemas=OAuth2PasswordBearer(tokenUrl='auth/login')


JTI='jti'
ROLE='role'
TYPE='type'
SUB='sub'
EXP='exp'


def PasswordHashed(password: str):
    h=ph.hash(password)
    return h


def PasswordVerifi(hash,password: str):
    try:
        ph.verify(hash,password)
        return True
    except VerifyMismatchError:
        return False


async def create_token(user_id: int,
                token_type,expires_delta):

    payload ={
        SUB: str(user_id),
        EXP: datetime.now(timezone.utc)+timedelta(minutes=expires_delta),
        TYPE : token_type,
        JTI : str(uuid.uuid4())
    }

    token=jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return token



async def current_token(r: redis,token: str=Depends(oauth_shemas)):

    async with _semaphore:

        try:
            payload=jwt.decode(token,settings.PUBLIC_KEY,algorithms=[settings.ALGORITHM])
                      
            key=f'black_list:{payload[JTI]}'

            black_list=await r.get(key)
           
            if black_list:
                logging.info('токен невалидный')
                raise HTTPException(status_code=400,detail='зайдите снова')
            
            if payload[TYPE] != 'access':
                logging.info('тип токена неправильный ')
                raise HTTPException(status_code=401,detail='ожидался access ')
            logging.info('токен успешно прошел ')

        
            return {'id': int(payload[SUB]),'type': payload[TYPE]}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401,detail='Токен истек')

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401,detail='невалидный токен')



    
   
        
async def logout(payload, r: redis):
    logging.info('выходбвызван logout')
    key=f'black_list:{payload[JTI]}'
    if payload[TYPE]!='access':
        raise HTTPException(status_code=401,detail='нужен токен access')

    current_time=datetime.now(timezone.utc).timestamp()
    ttl=int(payload[EXP]-current_time)
    
    if ttl>0:
        logging.info('токен удален')
        await r.set(key,1,ttl)
    
    