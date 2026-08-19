from argon2 import PasswordHasher
from config import settings,Role
import jwt
from datetime import timedelta,timezone,datetime
from fastapi  import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
import uuid
from argon2.exceptions import VerifyMismatchError

ph=PasswordHasher()

oauth_shemas=OAuth2PasswordBearer(tokenUrl='auth/login')

JTI='jti'
ROLE='role'
TYPE='type'
SUB='sub'
EXP='exp'


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


def create_token(user_id: int,
                token_type,expires_delta,role,
                seller_id: int|None=None,
                buyer_id: int|None=None):

    payload ={
        SUB: str(user_id),
        Role.SELLER: seller_id,
        Role.BAYER: buyer_id, 
        ROLE: role,
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

def current_token(token: str=Depends(oauth_shemas)):

    p=decode_token(token)
    if p[TYPE]!='access':
        raise HTTPException(status_code=401,detail='ожидался access ')
    
    if p[JTI] in black_list:
        raise HTTPException(status_code=400,detail='зайдите снова')
    
    if not all((p[SUB],p[ROLE])):
        raise HTTPException(status_code=404,detail='зайдите снова')

    if not p[Role.BAYER] and not p[Role.SELLER]:
        raise HTTPException(status_code=404, detail='зайдите снова')

    if p[Role.BAYER] and p[Role.SELLER]:
        return {'id': int(p[SUB]), ROLE:p[ROLE], Role.SELLER: p[Role.SELLER], Role.BAYER: p[Role.BAYER]}

    if p[Role.SELLER]:
        return {'id': int(p[SUB]), ROLE:p[ROLE], Role.SELLER: p[Role.SELLER]}

    return {'id': int(p[SUB]), ROLE:p[ROLE], Role.BAYER: p[Role.BAYER]}
    
        
def logout(payload):

    if payload[TYPE]!='access':
        raise HTTPException(status_code=401,detail='нужен токен access')
    
    black_list.add(payload[JTI])
    