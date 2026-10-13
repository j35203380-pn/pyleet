from app.auth.service.utils import JwtService
from app.auth.settings.base import jwt_conf
from app.auth.security.login import JWTUtils
from app.redis_client import RedisConnect
from app.auth.dependcies.auth import oauth_schemas
from fastapi import Depends




def jwt_services(r=Depends(RedisConnect)):
    return JwtService(utils=JWTUtils(),r=r,settings=jwt_conf)



async def current_token(serv:JwtService = Depends(jwt_services),token=Depends(oauth_schemas)):
    return await serv.current_token(token=token)








