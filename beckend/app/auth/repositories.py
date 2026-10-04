from app.database.db import AsyncSession 
from app.database.db import AsyncSession
from sqlalchemy import insert,select,or_
from app.exceptions import UserNotFound
from app.database.models import User
import asyncio
import logging





LimitDB=asyncio.Semaphore(20)


class AuthRepositories:

    def __init__(self,db: AsyncSession):

        self._db=db



    async def UserAdd(self,us: dict):
        async with LimitDB:

            
            async with self._db.begin():

                await self._db.execute(
                    insert(User)
                    .values(**us)
                )
            
            
            
    async def UserLogin(self,username: str):

        async with LimitDB:
            
            logging.info('в процессе UserLogin')
            async with self._db.begin():

                us=await self._db.execute(
                    select(User.id,User.password)
                    .where(or_(
                            User.nik_name==username,
                            User.email==username)))
                user=us.one_or_none()
                
                if not user:
                    raise UserNotFound()
        
        return user
