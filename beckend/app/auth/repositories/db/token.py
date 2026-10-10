from sqlalchemy import select,delete,update
from app.database.models import Session
from app.auth.repositories.db.base import BaseRepositories





class RefreshTokenRepo(BaseRepositories):
        
    async def insert_session(self, session):
        
        await self._db.add(session)



    async def get_session(self,token_hash: bytes):

        
        t=await self._db.execute(
                select(Session)
                    .where(Session.token_hash == token_hash))
            
        token=t.scalar_one_or_none()
        return token


    async def update_session(self,token_hash):
        t=await self._db.execute(
            select(Session)
                .where(Session.token_hash==token_hash))

        token=t.scalar_one_or_none()


    async def delete_all_sessions(self,user_id):

        await self._db.execute(
                delete(Session).where(Session.user_id == user_id)
                 )
        return

        
    async def del_session(self,token_hash: bytes):
        await self._db.execute(
            delete(Session).where(Session.token_hash == token_hash)
        )
        return 
              