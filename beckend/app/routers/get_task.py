from fastapi import APIRouter,HTTPException,Depends,status
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.dependcies import ReschePoints
from typing import Annotated
from app.routers.repositories import TaskRepositories 
from app.redis_client import RedisConnect,RedisCache
from redis.asyncio import Redis
from app.database.shemas.task_shemas import CategoriesItemList,TaskListItemGet,TaskDetailGet
from config import DifficultyLevel
import logging

routers = APIRouter(prefix='/problems',
                    tags=["Каталог Задач"])




def connect_db(db : AsyncSession= Depends(get_db)):
    return TaskRepositories(db)


def connect_redis(redis: Annotated[Redis, Depends(RedisConnect)]):
    return RedisCache(
        redis=redis,
        prefix='tasks',
    )


CurrenUser = Annotated[dict,Depends(current_token)]
GetDb = Annotated[TaskRepositories,Depends(connect_db)]
Cache = Annotated[RedisCache,Depends(connect_redis)]



@routers.get('/task/solution/{task_id}',response_model=TaskDetailGet)
async def solution_task(task_id: int, db: GetDb,r: Cache):
    
    logging.info(f'запрос task/solution/task_id-get_task')

    task=await r.get_cache(enum_id=task_id,model=TaskDetailGet)
    if not task:
        lock=r.lock_key(enum_id=task_id)
        async with lock:
            task=await r.get_cache(enum_id=task_id,model=TaskDetailGet)
            if not task:
                task=await db.GetTask(task_id=task_id)
                await r.set_cache(task_id,task)
    logging.info('task/solution/task_id-get_task запрос прошле бд ')
    return task




@routers.get('/task/{level}',response_model=list[TaskListItemGet])
async def get_task(level: DifficultyLevel , db: GetDb, r: Cache):
    logging.info(f'отпарвлен запрос task/level-get_task')
    result=await r.get_cache(enum_id=level,model=TaskListItemGet)
    if result: return result
    lock=r.lock_key(enum_id=level)
    async with lock:
        result=await r.get_cache(enum_id=level,model=TaskListItemGet)
        if result: return result
        result = await db.LevelTask(level=level)
        await r.set_cache_list(enum_id=level,pow=result,model=TaskListItemGet)

    return result



