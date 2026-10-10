from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from app.auth.service.utils import JwtService
from app.auth.security.login import JWTUtils
from app.redis_client import RedisConnect
from app.auth.security.auth import CryptoAuth
from app.auth.service.crypto import CryptoService
from app.auth.service.user import UserAuthService
from app.auth.service.database import DbService
from app.auth.repositories.db import AuthRepositories ,RefreshTokenRepo
from app.database.db import get_db
from fastapi import Depends
from app.auth.settings.base import jwt_conf
from typing import Annotated


oauth_schemas=OAuth2PasswordBearer(tokenUrl='/auth/login')

crypto_graph=CryptoService(CryptoAuth)



def jwt_services(r=Depends(RedisConnect)):
    return JwtService(utils=JWTUtils(),r=r,settings=jwt_conf)


def db_conn(db=Depends(get_db)):
    auth_r =AuthRepositories(db)
    token_r=RefreshTokenRepo(db)
    return DbService(auth_repo=auth_r, token_repo=token_r,db=db)


async def current_token(serv:JwtService = Depends(jwt_services),token=Depends(oauth_schemas)):
    return await serv.current_token(token=token)



def services_auth(db = Depends(db_conn),jwt_serv=Depends(jwt_services)):

    return UserAuthService(repo=db,jwt_=jwt_serv,crypt_=crypto_graph)




AuthServ=Annotated[UserAuthService,Depends(services_auth)]
UsReqForm=Annotated[OAuth2PasswordRequestForm,Depends()]

