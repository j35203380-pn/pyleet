from app.database.db import AsyncSession 
from app.database.db import AsyncSession,engine
from sqlalchemy import insert,select,or_
from app.exceptions import UserNotFound
from app.database.models import User
import asyncio
import logging


logger = logging.getLogger(__name__)



_semaphore=asyncio.Semaphore(20)


class AuthRepositories:

    def __init__(self,db: AsyncSession):

        self._db=db



    async def user_add(self,us: dict):
       
        async with _semaphore:
            
            async with self._db.begin():

                await self._db.execute(
                    insert(User)
                    .values(**us)
                )
  
            
            
    async def user_login(self,username: str):

        async with _semaphore:
            
          async with self._db.begin():

                us=await self._db.execute(
                    select(User.id, User.nik_name, User.password)
                    .where(or_(
                            User.nik_name==username,
                            User.email==username)))
                user=us.one_or_none()
        
        return user
