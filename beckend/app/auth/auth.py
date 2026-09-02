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

redis=Annotated[Redis,Depends(RedisConnect)]


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


def create_token(user_id: int,
                token_type,expires_delta):

    payload ={
        SUB: str(user_id),
        EXP: datetime.now(timezone.utc)+timedelta(minutes=expires_delta),
        TYPE : token_type,
        JTI : str(uuid.uuid4())
    }

    token=jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return token



def decode_token(token: str):
    try:
        return jwt.decode(token,settings.PUBLIC_KEY,algorithms=[settings.ALGORITHM])

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail='Токен истек')

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail='невалидный токен')



def current_token(r: redis,token: str=Depends(oauth_shemas)):
    
    payload=decode_token(token)
    key=f'black_list:{payload[JTI]}'
    black_list=r.get(key)
    if black_list:
        raise HTTPException(status_code=400,detail='зайдите снова')
    
    if payload[TYPE] != 'access':
        raise HTTPException(status_code=401,detail='ожидался access ')
    
   
        
def logout(payload, r: redis):
    key=f'black_list:{payload[JTI]}'
    if payload[TYPE]!='access':
        raise HTTPException(status_code=401,detail='нужен токен access')
    
    ttl=int(payload[EXP]> datetime.now(timezone.utc).timestamp())
    
    if ttl>0:
        r.set(key,1,ttl)
    
    