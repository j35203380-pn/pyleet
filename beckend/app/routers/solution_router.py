from fastapi import APIRouter,Depends
from app.database.db import get_db,AsyncSession
from app.redis_client import RedisCache,RedisConnect
from app.brokers import broker,RabBroker
from typing import Annotated
from app.routers.repositories import UserSubRepositories,TaskRepositories
from app.auth.auth import current_token
from redis.asyncio import Redis,client
from faststream.rabbit import RabbitBroker,RabbitQueue,RabbitExchange
from app.database.shemas.task_shemas import (ExecutionResult,SubmissionCreate,
                                             SubmissionAccepted,SubmissionListItemGet,
                                             ExecutionRequest,TaskDetailGet,TaskDetailGetAll)
from uuid import UUID,uuid4
from app.routers.service import message_service
import asyncio
import logging
import msgspec

encodermg=msgspec.json.Encoder()

router=APIRouter(prefix='/solution',
                 tags=['Решать Задачи'],
                 dependencies=[Depends(current_token)])


redis= Annotated[Redis,Depends(RedisConnect)]


def connect_sub_db(db: Annotated[AsyncSession,Depends(get_db)]):
    return UserSubRepositories(db)


def connect_task_db(db: Annotated[AsyncSession,Depends(get_db)]):
    return TaskRepositories(db)



def connect_red(r: redis):
    return RedisCache(
        redis=r,prefix='task',ttl=60*60*5
    )

def connect_pubsub(r: redis):
    return  r.pubsub()

TASKDB= Annotated[TaskRepositories, Depends(connect_task_db)]
SUBDB= Annotated[UserSubRepositories, Depends(connect_sub_db)]
CurretUser= Annotated[dict, Depends(current_token)]
RedCache= Annotated[RedisCache, Depends(connect_red)]
PubSub= Annotated[client.PubSub, Depends(connect_pubsub)]


queue=RabbitQueue('solution.execute')
exchange=RabbitExchange('submission')





@router.post('/run/{task_id}')
async def submit_task(task_id: int,submission: SubmissionCreate
                      ,TaskDb: TASKDB,user: CurretUser,r: RedCache):
    
    """обязательно напишите  класс ,иначе не сработает
    пример:
    class Solution:
       def func():"""
    
    
    submission_id=str(uuid4())
    task=await r.get_cache(task_id,TaskDetailGetAll)

    if not task:
        logging.info('кеш пустой ,запрос в бд ')
        lock=r.lock_key(task_id)
        async with lock:
                task=await r.get_cache(task_id,TaskDetailGetAll)
                if not task:
                    pow=await TaskDb.GetTask(task_id=task_id)
                    logging.info('кеширование ответа')
                    task=TaskDetailGetAll.model_validate(pow)
                    await r.set_cache(task_id,task)
                    logging.info('успешно прошел кешированеи')

    logging.info("message=ExecuitonResult начинает обрабатывать ")
    message=message_service(task=task,mode="run",submission=submission.code)
    ms=encodermg.encode(message)
    logging.info("message=ExecuitonResult успешно обрабобтал ")
    logging.info('публикация решение клиента')
    await broker.publish(
                message=ms,queue=queue,
                exchange=exchange,
                correlation_id=submission_id
                )           
    logging.info('успешно отправлен решение')
    return submission_id







@router.post('/submit/{task_id}',response_model=SubmissionAccepted)
async def submit_task(task_id: int,submission: SubmissionCreate
                              ,TaskDb: TASKDB,SubDb: SUBDB,user: CurretUser,r: RedCache):
    
    """обязательно напишите  класс ,иначе не сработает
    пример:
    class Solution:
       def func():"""
    
    
    task=await r.get_cache(task_id,TaskDetailGetAll)
    
    if task: logging.info('чтение из кеша ')
    
    if not task:
       
        lock=r.lock_key(task_id)
        async with lock:
                task=await r.get_cache(task_id,TaskDetailGetAll)
                if not task:
                    print('чтение из бд')
                    pow=await TaskDb.GetTask(task_id=task_id)
                    task=TaskDetailGetAll.model_validate(pow)
                   
                    await r.set_cache(task_id,task)

    message=message_service(task=task,mode="submit",submission=submission.code)
  
    
    submission_id=await SubDb.SubmissionPost(
                        task_id=task_id,
                        user_id=user['id'],
                        message=message)   
   
    
    
    return dict(
        id=submission_id.id,
        status=submission_id.status,
        created_at=submission_id.creadet_at)






@router.get('/result/{submission_id}')
async def result_submit(submission_id: str,queue:PubSub,r: redis):
    logging.info('ожидаем ответ от брокера ')
    key=f'result:submission:{submission_id}'
    res=await r.get(key)
    if res: return ExecutionResult.model_validate_json(res).model_dump()
    await queue.subscribe(submission_id)
    try:
        logging.info('слушаем эфир редис')
        async with asyncio.timeout(3):
            async for message in queue.listen():
                print(message)
                if message['type'] == 'message':
                    sub=ExecutionResult.model_validate_json(message['data'])
                    
                    return {**sub.model_dump()}
                    
    except TimeoutError:
        ms=await r.get(key)
        if ms : 
            result=ExecutionResult.model_validate_json(ms)
        else:
            return {'status': 'timeout'}
    finally:
        try:
            await queue.unsubscribe(submission_id)
            await queue.aclose()
        except Exception as e:
            logging.warning(f'ошибка при закрытии pubsub {e}')

    return result