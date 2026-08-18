from app.database.models import Comments,Task,Seller,Proviso
from app.database.shemas.task_shemas import TaskPost,ProvisoPost
from fastapi import APIRouter,HTTPException,Depends,status
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.redis_client import *
from app.dependcies import ReschePoints
from typing import Annotated
from config import Role
from app.routers.repositories import UserRepositories 
from redis.asyncio import Redis


#для проверки доступа 
is_sellers = ReschePoints(Role.SELLER)


routers = APIRouter(prefix='/uptask',
                   dependencies=[Depends(is_sellers)])




def connect_db(db : AsyncSession= Depends(get_db)):
    return UserRepositories(db)


def connect_redis(redis: Redis= Depends(RedisConnect)):
    return RedisCache(
        redis=redis,
        prefix='tasks',
    )

CurrenUser = Annotated[dict,Depends(current_token)]
PostDb = Annotated[UserRepositories,Depends(connect_db)]
Cache = Annotated[RedisCache,Depends(connect_redis)]


@routers.post('/',status_code=status.HTTP_201_CREATED,
              dependencies=[Depends(is_sellers)])
async def post_task(task : TaskPost,proviso: ProvisoPost,
                    user: CurrenUser, db:PostDb):

    await db.post_task(tasks=task,proviso=proviso,user_id=user[Role.SELLER])
    




