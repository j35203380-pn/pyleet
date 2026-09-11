from config import settings
from sqlalchemy.orm import  DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine


DATABASE_URL=settings.DATABASE_URL



engine=create_async_engine(DATABASE_URL,
                           pool_size=20,
                           max_overflow=20,
                           pool_timeout=30,
                           pool_pre_ping=True,
                           pool_recycle=1800,
                           echo=False)

AsyncLocal=async_sessionmaker(bind=engine,
                              class_=AsyncSession,
                              expire_on_commit=False)

class Base(DeclarativeBase):
    pass




