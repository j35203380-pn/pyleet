from faststream import FastStream,ContextRepo
from faststream.rabbit import RabbitBroker
from config import settings
from contextlib import asynccontextmanager
from redis.asyncio import Redis,ConnectionPool
import asyncio
from isolate import broker
import aiodocker

@asynccontextmanager
async def lifespan(contex: ContextRepo):
    docker=aiodocker.Docker()
    contex.set_global('docker',docker)
    await broker.start()
    pool=ConnectionPool.from_url(
            url=settings.REDISE_URL,decode_responses=True)
    redis= await Redis(connection_pool=pool)
    contex.set_global('redis', redis)
    yield

    await broker.stop()
    await docker.close()
    await redis.aclose()
    await pool.aclose()

    
app=FastStream(broker,lifespan=lifespan)
