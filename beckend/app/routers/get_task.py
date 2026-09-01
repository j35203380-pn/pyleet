from fastapi import APIRouter,HTTPException,Depends,status
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.dependcies import ReschePoints
from typing import Annotated
from app.routers.repositories import UserRepositories 
from app.redis_client import RedisConnect,RedisCache


routers = APIRouter(prefix='/problems',
                    tags=["Комменты"],
                    dependencies=[Depends(current_token)])




def connect_db(db : AsyncSession= Depends(get_db)):
    return UserRepositories(db)


def connect_redis(redis: Annotated[Redis, Depends(RedisConnect)]):
    return RedisCache(
        redis=redis,
        prefix='tasks',
    )


CurrenUser = Annotated[dict,Depends(current_token)]
PostDb = Annotated[UserRepositories,Depends(connect_db)]
Cache = Annotated[RedisCache,Depends(connect_redis)]


