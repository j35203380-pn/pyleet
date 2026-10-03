from app.auth.security import hash_password,verify_password,create_token
from app.auth.repositories import AuthRepositories
from app.database.db import get_db
from dataclasses import dataclass
from fastapi import status
from sqlalchemy.exc import IntegrityError
from app.exceptions import UserNotFound
import asyncio



@dataclass(slots=True)
class UserAuthAdd:
    name: str
    nik_name: str
    email: str
    password: str
    password_confim: str

class UserAuthService:
    def __init__(self,db,repo: AuthRepositories):
        self._db=db
        self._conn=repo


    async def add_user(self,users: UserAuthAdd):
        password_hash=await asyncio.to_thread(hash_password,users.password)
        us=dict(
            name=users.name,nik_name=users.nik_name,
            email=users.email,password=password_hash
            )
        try:
            async for session in self._db():
                repo:AuthRepositories=self._conn(session)
                await repo.UserAdd(us=us)
            return status.HTTP_200_OK
        
        except IntegrityError:
            raise UserNotFound()

    async def get_user(self,username: str, password: str):
        async for session in self._db():
            repo: AuthRepositories=self._conn(session)
            id,hash_password=await repo.UserLogin(username=username)
        veryf_password=await asyncio.to_thread(verify_password,hash_password,password)
        if not veryf_password:
            raise UserNotFound()

        token=await create_token(user_id=id,token_type='access',expires_delta=30)

        return token


auth_service=UserAuthService(get_db,AuthRepositories)