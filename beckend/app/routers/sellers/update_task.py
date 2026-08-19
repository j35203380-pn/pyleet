from app.database.shemas.task_shemas import (TaskPost,ProvisoPost,TaskPatch)
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


routers = APIRouter(prefix='/task',
                    tags=['Добавление и обновление Задач'],
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



@routers.post('/',status_code=status.HTTP_201_CREATED)
async def post_task(task : TaskPost,user: CurrenUser, db:PostDb):

    return await db.PostTask(tasks=task,seller_id=user[Role.SELLER])
    



@routers.put('/{task_id}')
async def put_task(task_id: int,task: TaskPost ,user: CurrenUser, db: PostDb):
    return await db.UpdateTask(task_id=task_id,
                               seller_id=user[Role.SELLER],
                               task=task)



@routers.patch('/{task_id}')
async def patch_task(task_id: int, task: TaskPatch, user: CurrenUser,db: PostDb):
    return await db.UpdateTask(task_id=task_id,
                               seller_id=user[Role.SELLER],
                               task=task)



@routers.delete('/{task_id}')
async def delete_task(task_id: int,users: CurrenUser,db: PostDb):

    return await db.DeleteTask(task_id=task_id,
                               seller_id=users[Role.SELLER])  
    