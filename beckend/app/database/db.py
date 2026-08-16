from config import settings
from sqlalchemy.orm import  DeclarativeBase,Mapped,mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine


DATABASE_URL=settings.DATABASE_URL

#это для проверки потом нужно удлаить
#DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine=create_async_engine(DATABASE_URL)

AsyncLocal=async_sessionmaker(bind=engine,
                              class_=AsyncSession,
                              expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncLocal() as session:
        yield session

