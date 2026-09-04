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
from app.routers.service import determine_statuse
import asyncio
import logging

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
    
    "обязательно напишите  класс ,иначе не сработает"
    "пример:"
    "class Solution:"
    "   def func():"
    
    
    submission_id=str(uuid4())
    await r.cache_del(task_id)
    task=await r.get_cache(task_id,TaskDetailGetAll)
    if not task:
        logging.info('кеш пустой ,запрос в бд ')
        lock=r.lock_key(task_id)
        async with lock:
                task=await r.get_cache(task_id,TaskDetailGetAll)
                if not task:
                    task=await TaskDb.GetTask(task_id=task_id)
                    logging.info('кеширование ответа')
                    ctask=TaskDetailGetAll.model_validate(task)
                    await r.set_cache(task_id,ctask)
                    logging.info('успешно прошел кешированеи')

    logging.info("message=ExecuitonResult начинает обрабатывать ")
    message=ExecutionRequest(
                mode='run',
                code=submission.code,
                method_name=task.method_name,
                test_cases=task.test_cases
                )
    logging.info("message=ExecuitonResult успешно обрабобтал ")
    logging.info('публикация решение клиента')
    await broker.publish(
                message.model_dump_json(),queue=queue,
                exchange=exchange,
                correlation_id=submission_id
                )           
    logging.info('успешно отправлен решение')
    return submission_id




@router.get('/run/result/{submission_id}')
async def result_submit(submission_id: str,queue:PubSub,r: redis):
    logging.info('ожидаем ответ от брокера ')
    key=f'result:submission{submission_id}'
    await queue.subscribe(submission_id)
    try:
        logging.info('слушаем эфир редис')
        async with asyncio.timeout(10):
            async for message in queue.listen():
                print(message)
                if message['type'] == 'message':
                    sub=ExecutionResult.model_validate_json(message['data'])
                    statuse=await determine_statuse(sub.exit_code,sub.test_result)
                    return {**sub.model_dump(),'status': statuse}
                    
    except TimeoutError:
        ms=await r.get(key)
        if ms : return ExecutionResult.model_validate_json(ms)
        return {'status': 'timeout'}
    finally:
        await queue.unsubscribe(submission_id)
        await queue.aclose()
    



@router.post('/submit/{task_id}',response_model=SubmissionAccepted)
async def submit_task(task_id: int,submission: SubmissionCreate
                              ,TaskDb: TASKDB,SubDb: SUBDB,user: CurretUser,r: RedCache):
    
    """обязательно напишите  класс ,иначе не сработает
    пример:
    class Solution:
       def func():"""
    
    logging.info('code принято')
    task=await r.get_cache(task_id,TaskDetailGetAll)
    if not task:
        logging.info('в кеше нет данных,идем в бд ')
        lock=r.lock_key(task_id)
        async with lock:
                task=await r.get_cache(task_id,TaskDetailGetAll)
                if not task:
                    task=await TaskDb.GetTask(task_id=task_id)
                    tsk=TaskDetailGet.model_validate(task)
                    logging.info('запись в кеш')
                    await r.set_cache(task_id,tsk)
                    logging.info('успешно кеширован')
    logging.info('записываем данные в Submission db')
    submission_id=await SubDb.SubmissionPost(task_id=task_id,user_id=user['id'],submission=submission)   
    logging.info('запись Submission db успешно прошло')
    logging.info('подготовим message для брокера')
    message=ExecutionRequest(
        mode='submit',
        code=submission.code,
        method_name=task.method_name,
        test_cases=task.test_cases
    )
    logging.info('message готов,отдаем брокеру')
    await broker.publish(
        message.model_dump_json(),queue=queue,
        exchange=exchange,
        correlation_id=submission_id.id
    )
    logging.info('брокер успешно отправил данные')
    return dict(id=submission_id.id,
                status=submission_id.status,
                created_at=submission_id.creadet_at)



@router.get('/submit/result/{submission_id}')
async def result_submit(submission_id: str,SubDb: SUBDB,user: CurretUser,r: redis,queue: PubSub):
    await queue.subscribe(submission_id)
    key=f'result:submission{submission_id}'
    
    try:
        async with asyncio.timeout(10):
            async for message in queue.listen():
                if message['type']=='message':
                    sub=ExecutionResult.model_validate_json(message['data'])
                    statuse=await determine_statuse(sub.exit_code,sub.test_result)
                    await SubDb.SubmissionUpdate(submission_id=UUID(submission_id),user_id=user['id'],tasks=sub,statuse=statuse)
                    return  {**sub.model_dump(),'status': statuse}
                    
                

    except TimeoutError:
        result= await r.get(key)
        if not result:
            return {'status': 'timeout'}
        
        sub=ExecutionResult.model_validate_json(result)
        statuse=await determine_statuse(sub.exit_code,sub.test_result)
        await SubDb.SubmissionUpdate(submission_id=UUID(submission_id),user_id=user['id'],tasks=sub,statuse=statuse)
        return {**sub.model_dump(),'status': statuse}
        

    finally:
        await queue.unsubscribe(str(submission_id))
        await queue.aclose()