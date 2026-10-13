from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from app.auth.service import (JwtService,CryptoService,
                              UserTotpService,UserAuthService,
                              DbService,TokenService)
from app.auth.security.login import JWTUtils
from app.redis_client import RedisConnect
from app.auth.security.auth import CryptoAuth
from app.auth.repositories.db import AuthRepositories ,RefreshTokenRepo
from app.database.db import get_db
from fastapi import Depends
from app.auth.settings.base import jwt_conf
from typing import Annotated


oauth_schemas=OAuth2PasswordBearer(tokenUrl='/auth/login')

crypto_graph=CryptoService(CryptoAuth)



def jwt_services(r=Depends(RedisConnect)):
    return JwtService(utils=JWTUtils(),r=r,settings=jwt_conf)

def token_serv(r=Depends(RedisConnect)):
    return TokenService(cache=r)

def totp_serv(db=Depends(get_db)):
    totp_repo=AuthRepositories(db)
    return UserTotpService(repo_auth=totp_repo,db=db)

def db_conn(db=Depends(get_db)):
    auth_r =AuthRepositories(db)
    token_r=RefreshTokenRepo(db)
    return DbService(auth_repo=auth_r, token_repo=token_r,db=db)


async def current_token(serv:JwtService = Depends(jwt_services),token=Depends(oauth_schemas)):
    return await serv.current_token(token=token)


async def current_2fa_token(serv:JwtService = Depends(jwt_services),token=Depends(oauth_schemas)):
    return await serv._2fa_token(token=token)





def services_auth(db = Depends(db_conn),
                  jwt_serv=Depends(jwt_services),
                  tooken_serv=Depends(token_serv),
                  totr_=Depends(totp_serv)):

    return UserAuthService(repo=db,jwt_=jwt_serv,
                           crypt_=crypto_graph,
                           token_=tooken_serv,
                           totp_=totr_)



AuthService=Annotated[UserAuthService,Depends(services_auth)]

UsReqForm=Annotated[OAuth2PasswordRequestForm,Depends()]

