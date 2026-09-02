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


LimitDB=asyncio.Semaphore(20)


class AuthRepositories:

    def __init__(self,db: AsyncSession):

        self._db=db



    async def UserAdd(self,users: UserPost):
        
        password_hash=PasswordHashed(users.password)
        users.password=password_hash
        us=dict(
            name=users.name,nik_name=users.nik_name,
            email=users.email,password=password_hash
        )
        await self._db.execute(
            insert(User)
            .values(**us)
        )
        return status.HTTP_201_CREATED



    async def UserLogin(self,users: OAuth2PasswordRequestForm):
        us=await self._db.execute(
            select(User)
            .where(or_
                   (User.nik_name==users.username,
                    User.email==users.username)))
        user=us.scalars().first()
        if not user:
            raise UserNotFound()
        password=PasswordVerifi(user.password,users.password)
        if not password:
            raise InvalidPasswordException()
        token= create_token(user_id=user.id,token_type= 'access',expires_delta=30)
        if not token:
            raise UserNotFound()
        return token
