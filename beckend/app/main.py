from fastapi import FastAPI
from app.auth.login import router
from app.database.models.auth_models import User_auth
from app.database.models.user_models import Seller, Buyer
from app.database.models.task_models import Comments,Task,Proviso
from contextlib import asynccontextmanager
from app.database.db import engine,Base

@asynccontextmanager
async def lifaespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield 
    await engine.dispose()


app=FastAPI(lifespan=lifaespan)

app.include_router(router)

