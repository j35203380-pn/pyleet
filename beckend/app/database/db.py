from config import settings
from sqlalchemy.orm import  DeclarativeBase,Mapped,mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine


DATABASE_URL=settings.DATABASE_URL

#во время тестирование подлючите sqlite
#DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine=create_async_engine(DATABASE_URL,
                           pool_size=10,
                           max_overflow=10,
                           pool_timeout=30,
                           pool_pre_ping=True,
                           pool_recycle=1800,
                           echo=False)

AsyncLocal=async_sessionmaker(bind=engine,
                              class_=AsyncSession,
                              expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncLocal() as session:
        yield session



async def test_base():
    async with engine.begin() as conn:
         await conn.run_sync(Base.metadata.create_all)