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
                                             ExecutionRequest,TaskDetailGet)
from uuid import UUID,uuid4
from app.routers.service import determine_statuse
import asyncio


router=APIRouter(prefix='/TaskSolution',
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
    submission_id=str(uuid4())
    task=await r.get_cache(task_id,TaskDetailGet)
    if not task:
        lock=r.lock_key(task_id)
        async with lock:
                task=await r.get_cache(task_id,TaskDetailGet)
                if not task:
                    task=await TaskDb.GetTask(task_id=task_id)
                    await r.set_cache(task_id,task)

       
    message=ExecutionRequest(
                mode='run',
                code=submission.code,
                method_name=task.method_name,
                test_cases=task.test_cases
                )
    
    await broker.publish(
                message.model_dump_json(),queue=queue,
                exchange=exchange,
                correlation_id=submission_id
                )           
    return submission_id




@router.get('/run/result/{submission_id}',response_model=ExecutionResult)
async def result_submit(submission_id: UUID,r:PubSub):
    
    await r.subscribe(submission_id)
    try:
        async with asyncio.timeout(60):
            async for message in r.listen():
                if message['type'] == 'message':
                    sub=ExecutionResult.model_validate_json(message['data'])
                    statuse=determine_statuse(sub.exit_code,sub.test_result)
                    return {**sub.model_dump(),'status': statuse}
                    
    except TimeoutError:
        return {'status': 'timeout'}
    finally:
        await r.unsubscribe(submission_id)
        await r.aclose()
    



@router.post('/submit/{task_id}',response_model=SubmissionAccepted)
async def submit_task(task_id: int,submission: SubmissionCreate
                              ,TaskDb: TASKDB,SubDb: SUBDB,user: CurretUser,r: RedCache):
    
    task=await r.get_cache(task_id,TaskDetailGet)
    if not task:
        lock=r.lock_key(task_id)
        async with lock:
                task=await r.get_cache(task_id,TaskDetailGet)
                if not task:
                    task=await TaskDb.GetTask(task_id=task_id)
                    await r.set_cache(task_id,task)

    submission_id=await SubDb.SubmissionPost(task_id=task_id,user_id=user['id'],submission=submission)   
    message=ExecutionRequest(
        mode='submit',
        code=submission.code,
        method_name=task.method_name,
        test_cases=task.test_cases
    )
    
    await broker.publish(
        message.model_dump_json(),queue=queue,
        exchange=exchange,
        correlation_id=submission_id.id
    )
    return submission_id


@router.get('/submit/result/{submission_id}',response_model=ExecutionResult)
async def result_submit(submission_id: UUID,SubDb: SUBDB,user: CurretUser,r: redis,queue: PubSub):
    await queue.subscribe(str(submission_id))
    key=f'result:submission{submission_id}'
    
    try:
        async with asyncio.timeout(60):
            async for message in queue.listen():
                if message['type']=='message':
                    sub=ExecutionResult.model_validate_json(message['data'])
                    statuse=await determine_statuse(sub.exit_code,sub.test_result)
                    await SubDb.SubmissionUpdate(submission_id=submission_id,user_id=user['id'],tasks=sub,statuse=statuse)
                    return  {**sub.model_dump(),'status': statuse}
                    
                

    except TimeoutError:
        result= await r.get(key)
        if not result:
            return {'status': 'timeout'}
        
        sub=ExecutionResult.model_validate_json(result)
        statuse=await determine_statuse(sub.exit_code,sub.test_result)
        await SubDb.SubmissionUpdate(submission_id=submission_id,user_id=user['id'],tasks=sub,statuse=statuse)
        return {**sub.model_dump(),'status': statuse}
        

    finally:
        await queue.unsubscribe(str(submission_id))
        await queue.aclose