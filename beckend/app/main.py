from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from app.auth.login import router as router_auth
from contextlib import asynccontextmanager
from redis.asyncio import Redis,ConnectionPool
from config import settings
from app.routers import approuter as routers_rout
from app.exceptions import AllExceptions
import logging,traceback
from app.redis_client import RateLimite
from app.brokers.connection import broker 
from app.Admin.models import UserAdminTask,UserAdminCategory,authenfication_backend
from sqladmin import Admin
from app.database.db import engine,Base
from app.workers.outbox_relay import outbox_res

import asyncio

print(broker)
print(broker.routers)
print(broker.subscribers)
@asynccontextmanager
async def lifespan(app:FastAPI):
       
    await broker.start()
    outbox_task=asyncio.create_task(outbox_res())
    
    pool=ConnectionPool.from_url(
        url=settings.REDISE_URL,decode_responses=True
    )
    
    redis=Redis(connection_pool=pool)
    limite=RateLimite(redis=redis)
    app.state.limite=limite
    app.state.redis=redis

    yield 
    outbox_task.cancel()
    try:
        await outbox_task
    except asyncio.CancelledError:
        pass

    await broker.stop()
    await redis.aclose()
    await pool.aclose()


app=FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(routers_rout)





@app.middleware('http')
async def rate_limite(request: Request,call_next):
    limite=request.app.state.limite
    client=request.client.host if request.client else 'uknown'
    endpoint=request.url.path
    if endpoint in ['/docs','/openapi.json','/redoc']:
        return await call_next(request)
    is_block=await limite.is_limite(
        endpoint=request.url.path,ip_adress=client,
        max_request=5,window_second=5)
    if is_block:
        return JSONResponse(status_code=429,content='заработал рате лимите')

    return await call_next(request)
    

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger("fastapi_exceptions")

@app.exception_handler(AllExceptions)
async def exceptions_all(req: Request, exc: AllExceptions):
    error_tr=traceback.format_exc()

    logger.error(
        f'Ошибка при запросе к {req.url.path}\n'
        f'Детали: {exc.detail} (Статус: {exc.status_code})\n'
        f"Трейсбек: {error_tr}"
    )
    return JSONResponse(exc.detail,status_code=exc.status_code)


admin=Admin(app,engine,authentication_backend=authenfication_backend)
admin.add_view(UserAdminTask)
admin.add_view(UserAdminCategory)