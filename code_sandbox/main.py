from faststream import FastStream,ContextRepo
from faststream.rabbit import RabbitBroker
from config import settings
from contextlib import asynccontextmanager
from redis.asyncio import Redis,ConnectionPool
from isolated.subscribe import brokersub
import aiodocker

broker=RabbitBroker(settings.RABBIT_BROKER_URL)
broker.include_router(brokersub)

@asynccontextmanager
async def lifespan(contex: ContextRepo):

    docker=aiodocker.Docker()
    contex.set_global('docker',docker)
   
    pool=ConnectionPool.from_url(
            url=settings.REDISE_URL,decode_responses=True)
    redis= await Redis(connection_pool=pool)
    contex.set_global('redis', redis)

    yield

    await docker.close()
    await redis.aclose()
    await pool.aclose()

    
app=FastStream(broker,lifespan=lifespan)
