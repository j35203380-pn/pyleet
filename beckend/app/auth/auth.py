from argon2 import PasswordHasher
from config import settings
import jwt
from datetime import timedelta,timezone,datetime
from fastapi  import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
import uuid
from argon2.exceptions import VerifyMismatchError

ph=PasswordHasher()

oauth_shemas=OAuth2PasswordBearer(tokenUrl='auth/login')


def hashed(password: str):
    h=ph.hash(password)
    return h


black_list=set()

def verifi(hash,password: str):
    try:
        ph.verify(hash,password)
        return True
    except VerifyMismatchError:
        return False


def create_token(user_id: int, token_type,expires_delta,role):

    payload ={
        'sub': str(user_id),
        'role': role,
        'exp': datetime.now(timezone.utc)+timedelta(minutes=expires_delta),
        'type' : token_type,
        'jti' : str(uuid.uuid4())
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

def current_token(token: str=Depends(oauth_shemas)):

    p=decode_token(token)
    if p['type']!='access':
        raise HTTPException(status_code=401,detail='ожидался access ')
    if p['jti'] in black_list:
        raise HTTPException(status_code=400,detail='зайдите снова')
    return p

def logout(payload):
    if payload['type']!='access':
        raise HTTPException(status_code=401,detail='нужен токен access')
    black_list.add(payload['jti'])
    