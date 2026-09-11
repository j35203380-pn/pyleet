from app.database.db import AsyncSession 
from app.database.db import AsyncSession
from sqlalchemy import insert,select,or_
from sqlalchemy.orm import joinedload
from app.database.shemas.auth_shemas import UserPost
from fastapi import status
from app.exceptions import InvalidPasswordException ,UserNotFound
from app.database.models import User
from app.auth.auth import PasswordHashed,PasswordVerifi,create_token
from fastapi.security import OAuth2PasswordRequestForm
import asyncio
import logging
from dataclasses import dataclass

@dataclass(slots=True)
class UserAuthAdd:
    name: str
    nik_name: str
    email: str
    password: str
    password_confim: str


LimitDB=asyncio.Semaphore(20)


class AuthRepositories:

    def __init__(self,db: AsyncSession):

        self._db=db



    async def UserAdd(self,users: UserAuthAdd):
        async with LimitDB:

            logging.info('в процессе UserAdd')

            password_hash=await asyncio.to_thread(PasswordHashed,users.password)
        
            us=dict(
                name=users.name,nik_name=users.nik_name,
                email=users.email,password=password_hash
            )
            async with self._db.begin():

                await self._db.execute(
                    insert(User)
                    .values(**us)
                )
            
            logging.info('UserAdd прошел успешно')
            return status.HTTP_201_CREATED



    async def UserLogin(self,users: OAuth2PasswordRequestForm):

        async with LimitDB:
            
            logging.info('в процессе UserLogin')
            us=await self._db.execute(
                select(User)
                .where(or_(
                        User.nik_name==users.username,
                        User.email==users.username)))
            user=us.scalar_one_or_none()
            if not user:
                raise UserNotFound()
            password=await asyncio.to_thread(PasswordVerifi,user.password,users.password)
        if not password:
            raise InvalidPasswordException()
        token= await create_token(user_id=user.id,token_type= 'access',expires_delta=30)
        if not token:
            raise UserNotFound()
        logging.info('UserLogin прошел успешно')
        return token
