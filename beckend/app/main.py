from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from app.auth.login import router as router_auth
from app.database.models.auth_models import User_auth
from app.database.models.user_models import Seller, Buyer
from app.database.models.task_models import Comments,Task,Proviso
from contextlib import asynccontextmanager
from app.database.db import engine,Base
from redis.asyncio import Redis,ConnectionPool
from config import settings
from app.routers import approuter as routers_rout
from app.exceptions import AllExceptions
import logging,traceback


@asynccontextmanager
async def lifespan(app:FastAPI):
    pool=ConnectionPool.from_url(
        url=settings.REDISE_URL,decode_responses=True
    )
    redis=Redis(connection_pool=pool)

    app.state.redis=redis

    yield 

    await redis.aclose()
    await pool.aclose()


app=FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(routers_rout)


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
