from config import settings
from faststream import Context,AckPolicy
from faststream.rabbit import RabbitBroker,RabbitQueue,RabbitExchange,RabbitMessage
from typing import Annotated
from redis.asyncio import Redis
from faststream.rabbit.schemas import Channel
import time
import  aiodocker
import asyncio
from code_sandbox.shemas import ExecutionResult,ConfDcoker,ExecutionRequest
from code_sandbox.harness import build_script
import json


LimitSem=asyncio.Semaphore(15)

broker=RabbitBroker(settings.RABBIT_BROKER_URL)
queue=RabbitQueue('solution.execute')
exchange=RabbitExchange('submission')

redis=Annotated[Redis,Context('redis')]

docker=aiodocker.Docker()


@broker.subscriber(queue=queue,exchange=exchange,channel=Channel(prefetch_count=30),ack_policy=AckPolicy.MANUAL)
async def run_code(msg: RabbitMessage,r: redis):
    
    body=ExecutionRequest.model_validate_json(msg.body)
    correlation_id=str(msg.correlation_id)
    result= await isolate(body.code,body.method_name,body.test_cases,timeout=3)
    
    exc=ExecutionResult(**result)
    if body.mode == 'submit':
        key=f'result:submission{correlation_id}'
        await r.set(key,exc.model_dump_json(),ex=90)
    await r.publish(correlation_id,exc.model_dump_json())
    await msg.ack()




async def isolate(code :str, timeout: int,method : str,test_code: str):
    start=time.monotonic()
    container=await docker.containers.create(config=ConfDcoker)

    try:
        async with LimitSem:
            stream=await container.attach(stdin=True)
            await container.start()
            code_user=await build_script(user_code=code,method_name=method,test_cases=test_code)
            await stream.write_in(code_user)
            await stream.close()

            try:

                await asyncio.wait_for(container.wait(timeout=timeout),timeout=timeout)

            except TimeoutError:
                await container.kill()

            log=await container.log(stdout=True,stderr=True)
            info=await container.show()
            exit_code=info['State']['ExitCode']

    finally:

        try:
            await container.delete()

        except aiodocker.exceptions.DockerError:
            pass

        


    tm=(time.monotonic()-start)*1000

    output=''.join(log)
    test_result=None
    if '###RESULT###' in output:
        json_part = output.split('###RESULT###')[-1].strip()
        try:
            test_result=json.loads(json_part)
        except json.JSONDecodeError:
            pass

    return dict(logs=log,
                 output=output,
                   exit_code=exit_code,
                     test_results=test_result,
                       time_ms=round(tm, 2))

    