from fastapi import APIRouter,HTTPException,Depends,status,BackgroundTasks
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.dependcies import ReschePoints
from typing import Annotated
from app.routers.repositories import CategoryRepositories 
from app.redis_client import RedisConnect,RedisCache
from redis.asyncio import Redis
from app.database.shemas.task_shemas import CategoriesItemList, CategoryAllGet,CategoryAllCreate
import  asyncio

routers = APIRouter(prefix='/category',
                    tags=["Категория"])




def connect_db(db : AsyncSession= Depends(get_db)):
    return CategoryRepositories(db)


def connect_redis(redis: Annotated[Redis, Depends(RedisConnect)]):
    return RedisCache(
        redis=redis,
        prefix='category',
        ttl=60
    )


CurrenUser = Annotated[dict,Depends(current_token)]
GetDb = Annotated[CategoryRepositories,Depends(connect_db)]
Cache = Annotated[RedisCache,Depends(connect_redis)]






@routers.get('/category',response_model=list[CategoryAllGet])
async def category_get(db: GetDb,r: Cache,background_task: BackgroundTasks):
    key='all'
    result=await r.get_cache(enum_id=key)
    if result : return result,'cache'

    lock=r.lock_key(enum_id=key)
    async with lock:
        result=await r.get_cache(enum_id=key)
        if result : return result

        result= await db.CategoriesAll()
        await r.set_cache_list(enum_id=key,pow=result,
                                                 model=CategoryAllGet)
           
    return result


async def category_cache(key: str,pow: CategoryAllCreate,r: Cache):
    res=[CategoryAllGet.model_validate(item) for item in pow]
    await r.set_cache(enum_id=key,pow=res)




@routers.get('/task/{cat_id}',response_model=CategoriesItemList)
async def get_task(cat_id: int, db: GetDb, r: Cache):
    TASK='task'
    result=await r.get_cache(suffix=TASK, enum_id=cat_id)
    if result: return result
    lock=r.lock_key(suffix=TASK,enum_id=cat_id)
    async with lock:
        result=await r.get_cache(enum_id=cat_id)
        if  result: return result
        
        result=await db.CategoriesGet(cat_id=cat_id)
        res=CategoriesItemList.model_validate(result)
        await r.set_cache(suffix=TASK,enum_id=cat_id,pow=res)

    return result 

