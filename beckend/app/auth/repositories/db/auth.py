from sqlalchemy import insert,select,or_
from app.database.models import User
from app.auth.repositories.db.base import BaseRepositories





class AuthRepositories(BaseRepositories):



    async def insert_user(self,us: dict):


            await self._db.execute(
                            insert(User)
                            .values(**us)
                )
  
            
            
    async def select_user(self,username: str):

        
            us=await self._db.execute(
                        select(User.id, User.nik_name, User.password)
                        .where(or_(
                                User.nik_name==username,
                                User.email==username)))
            user=us.one_or_none()
        
            return user

