from config import settings
from faststream import Context,AckPolicy
from faststream.rabbit import RabbitBroker,RabbitQueue,RabbitExchange,RabbitMessage
from typing import Annotated
from redis.asyncio import Redis
from faststream.rabbit.schemas import Channel
import time
import logging
import aiodocker
import asyncio
from shemas import ExecutionResult,ConfDcoker,ExecutionRequest
from harness import build_script
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


LimitSem=asyncio.Semaphore(15)

broker=RabbitBroker(settings.RABBIT_BROKER_URL)
queue=RabbitQueue('solution.execute')
exchange=RabbitExchange('submission')

redis=Annotated[Redis,Context('redis')]

DOCKER=Annotated[aiodocker.Docker,Context('docker')]


@broker.subscriber(queue=queue,exchange=exchange,channel=Channel(prefetch_count=30),ack_policy=AckPolicy.MANUAL)
async def run_code(msg: RabbitMessage,r: redis,docker: DOCKER):

    print('начался брокер перехват сообщения')
    logging.info('запрос принят брокеров')
    body=ExecutionRequest.model_validate_json(msg.body)
    correlation_id=str(msg.correlation_id)
    print(correlation_id)
    result= await isolate_run(code=body.code,method=body.method_name,
                              test_code=body.test_cases,timeout=3,
                              docker=docker)
    logging.info('взять результаты контенйера')
    exc=ExecutionResult(**result)

    key=f'result:submission{correlation_id}'
    await r.set(key,exc.model_dump_json(),ex=90)
    await r.publish(correlation_id,exc.model_dump_json())
    logging.info('ответ отправлен')
    await msg.ack()




async def isolate_run(code :str, timeout: int,method : str,test_code: list[dict],docker: aiodocker.Docker):
    start=time.monotonic()
    logging.info('начинается контейне')
    container=await docker.containers.create(config=ConfDcoker)

    try:
        async with LimitSem:
            stream= container.attach(stdin=True)
            await container.start()
            logging.info('отправляем данные в скрипт builder_script')
            code_user=await build_script(user_code=code,method_name=method,test_cases=test_code)
            
            await stream.write_in(code_user.encode())
            await stream.close()
            logging.info('скрипт вернул успешно результаты')
            try:
                logging.info('ждем контейнера')
                    
                await asyncio.wait_for(container.wait(),timeout=timeout)
                logging.info('контейнер успешно обработал')
            except TimeoutError:
                await container.kill()

            log=await container.log(stdout=True,stderr=True)
            
            info=await container.show()
            print("CONTAINER STATE:", info["State"])
            exit_code=info['State']['ExitCode']

    finally:

        try:
            await container.delete()

        except aiodocker.exceptions.DockerError:
            pass

        


    tm=(time.monotonic()-start)*1000

    output=''.join(log)
    test_result=None
    lines= output.splitlines()
    try:
        result_index=lines.index("###RESULT###")
        json_part = lines[result_index+1].strip()
        test_result=json.loads(json_part)
    
    except (ValueError, IndexError, json.JSONDecodeError):
        logging.exception("Не удалось распарсить test_result")
    logging.info('контейнер закончил')
    s=dict(logs=log,
                 output=output,
                   exit_code=exit_code,
                     test_result=test_result,
                       time_ms=round(tm, 2))
    
    return s
    