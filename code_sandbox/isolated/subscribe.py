from faststream import Context,AckPolicy
from faststream.rabbit import RabbitBroker,RabbitRouter,RabbitQueue,RabbitExchange,RabbitMessage
from typing import Annotated
from faststream.rabbit.schemas import Channel
from shemas import ExecutionRequest,ExecutionDocker,ExecutionResult
from isolated.isolate import isolate_run
from redis.asyncio import Redis
from isolated.service import determine_statuse
from isolated.publish import publish_run
import aiodocker
import msgspec
import asyncio
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)




decoder=msgspec.json.Decoder(type=ExecutionRequest)
encoder=msgspec.json.Encoder()

RabBroker=Annotated[RabbitBroker,Context('broker')]
DOCKER=Annotated[aiodocker.Docker,Context('docker')]
redis=Annotated[Redis,Context('redis')]

brokersub=RabbitRouter()

QUEUE_EXEC=RabbitQueue('solution.execute')
EXCHANGE=RabbitExchange('submission')



@brokersub.subscriber(queue=QUEUE_EXEC,exchange=EXCHANGE,
                      channel=Channel(prefetch_count=40),
                      ack_policy=AckPolicy.NACK_ON_ERROR)
async def sub_out(msg: RabbitMessage,br: RabBroker,docker: DOCKER,r: redis):

    logging.info('запрос принят брокероm')
    logging.info('декодирования')
    
    data=decoder.decode(msg.body)
    
    logging.info('декодирования прошло успешно')
    logging.info('передаем в изолятор')
    
    result=await isolate_run(code=data.code,
                                    method=data.method_name,
                                    test_code=data.test_cases,
                                    timeout=3,
                                    docker=docker)

    if not result:
        raise RuntimeError(f"не смог выполнить submission\
                            {correlation_id}— инфраструктурный сбой")

    logging.info('изолятор успешно закончился ')
    logging.info('получаем статус')
            
    status=determine_statuse(exit_code=result.get('exit_code'),
                             test_results=result.get('test_result'))

    logging.info(f'статус получен {status}')
    logging.info('передаем в encode')
        
    sub=encoder.encode(ExecutionResult(**result,status=status))
    correlation_id=str(msg.correlation_id)

    key=f'result:submission:{correlation_id}'

    logging.info('encode прошла успешно')
    logging.info('передаем в публикацию')
        
    async with asyncio.TaskGroup() as ts:
        if data.mode=='submit':
            ts.create_task(publish_run(message=sub,key=correlation_id,broker=br))
        
        ts.create_task(r.set(key, sub, ex=90))
        ts.create_task(r.publish(key,sub))

    logging.info('публикация прошла успешно')
    logging.info('isolator закончил работу')
        
                

