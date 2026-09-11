from faststream import Context
from faststream.rabbit import RabbitBroker,RabbitExchange,RabbitQueue
from typing import Annotated
import asyncio



RabBroker=Annotated[RabbitBroker,Context()]
LIMIT_BR=50
EXCHANGE=RabbitExchange('submission')
QUEUE_RES=RabbitQueue('solution.result')

_semaphore=asyncio.Semaphore(LIMIT_BR)

async def publish_run(message: bytes,key: str, 
                      broker: RabbitBroker):
    async with _semaphore:
        await broker.publish(
            message=message,
            queue=QUEUE_RES,
            exchange=EXCHANGE,
            correlation_id=key
        )

