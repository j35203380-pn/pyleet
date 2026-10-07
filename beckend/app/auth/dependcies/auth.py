from fastapi.security import OAuth2PasswordBearer
from app.auth.service.utils import JwtService,expire
from app.auth.security.login import JWTUtils
from app.redis_client import RedisConnect
from app.auth.service.user import UserAuthService
from app.auth.repositories.repositories import AuthRepositories
from app.database.db import get_db
from fastapi import Depends


oauth_schemas=OAuth2PasswordBearer(tokenUrl='/auth/login')


def jwt_services(r=Depends(RedisConnect)):
    return JwtService(utils=JWTUtils(),r=r,expire=expire)


def db_conn(db=Depends(get_db)):
    return AuthRepositories(db)


async def current_token(serv:JwtService =Depends(jwt_services),token=Depends(oauth_schemas)):
    return await serv.current_token(token=token)



def services_auth(db = Depends(db_conn),jwt_serv=Depends(jwt_services)):

    return UserAuthService(repo=db,jwt_=jwt_serv)

