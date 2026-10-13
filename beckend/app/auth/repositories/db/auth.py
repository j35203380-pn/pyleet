from sqlalchemy import insert,select,or_,update
from app.database.models import User,UserTOTP
from sqlalchemy.orm import joinedload
from app.auth.repositories.db.base import BaseRepositories





class AuthRepositories(BaseRepositories):



    async def insert_user(self,us: dict):


            await self._db.execute(
                            insert(User)
                            .values(**us)
                )
  
            
            
    async def select_user(self,username: str):
        

        
            us=await self._db.execute(
                        select(User)
                        .options(joinedload(User.totp).load_only(UserTOTP.enable))
                        .where(or_(
                                User.nik_name==username,
                                User.email==username)))
            user=us.scalar_one_or_none()
        
            return user


    async def insert_totp(self,data: dict):
           
           await self._db.execute(
                  insert(UserTOTP)
                  .values(**data))


    async def select_totp(self,user_id):
           
           us=await self._db.execute(
                  select(UserTOTP)
                  .where(UserTOTP.user_id == user_id)
                  .with_for_update()
           )

           return us.scalar_one_or_none()
           



   