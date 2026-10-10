from app.auth.repositories.db import AuthRepositories,RefreshTokenRepo
from app.exceptions import UserNotFound,UserTokenError
from app.auth.schemas.token import SessionAddDTO,SessionUpdDTO
from app.database.models.auth_models import Session
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio,time

_semaphore=asyncio.Semaphore(15)


class DbService:

    def __init__(
                    self,auth_repo: AuthRepositories,
                    token_repo: RefreshTokenRepo,
                    db : AsyncSession
        ):
        
        self._auth_db=auth_repo
        self._token_repo=token_repo
        self._db=db


    async def user_add(self,us: dict):
        try:
                
            async with _semaphore:
                async with self._db.begin():
                    await self._auth_db.insert_user(us)
            return {"statuse": "200 OK"}

        except Exception as e:
            raise e
  
            
            
    async def user_login(self,username: str):
        
        async with _semaphore:
            async with self._db.begin():
                user=await self._auth_db.select_user(username)
                

        if not user:
            raise UserNotFound()

        return user
        

    async def session_add(self, sessions: SessionAddDTO):
                
        
        
        sess=Session(user_id=sessions.user_id,
                    abs_expire=sessions.abs_expire,
                    user_agent=sessions.user_agent,
                    ip_adress=sessions.ip_adress,
                    token=sessions.token_hash)
        try:
                
            async with _semaphore:
                async with self._db.begin():
                    await self._token_repo.insert_session(session=sess)
            return 
        
        except Exception as e:
            raise e



    async def session_validate_tokens(self,token_hash: bytes):
        
        async with self._db.begin():
            token: Session|None=await self._token_repo.get_session(token_hash)
            
            if not token:
                raise UserTokenError()
            
        if token.revoked:
            async with self._db.begin():
                await self._token_repo.delete_all_sessions(token.user_id)
            raise UserTokenError()
            

        elif not token.is_active or token.abs_expire<int(time.time()):
                raise UserTokenError()
        
        return token 


    async def session_update_token(self, token_hash,sess: SessionUpdDTO):


        async with self._db.begin():
            token:Session=await self._token_repo.update_session(token_hash)
            token.token_hash=sess.token_hash
            token.ip_adress=sess.ip_adress
            token.user_agent=sess.user_agent

        return

        


    async def del_token(self,token_hash):
        
        async with self._db.begin():
            await self._token_repo.del_session(token_hash)
        raise UserTokenError()

        
            
        
        