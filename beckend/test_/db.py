from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from app.database.db import Base
from sqlalchemy.pool import StaticPool


TEST_DATABASE_URL='sqlite+aiosqlite:///:memory:'

test_engine=create_async_engine(TEST_DATABASE_URL,
                                poolclass=StaticPool,
                                connect_args={"check_same_thread": False})

test_aiomaker=async_sessionmaker(bind=test_engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)


async def init_test_base():
    async with test_engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

async def drop_test_base():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)