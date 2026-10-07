from app.database.db import AsyncLocal
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.repositories import UserSubRepo
from app.schemas.solution import SolCreate,SubPostAdd
from dataclasses import fields


class SolutionService:

    def __init__(self, repo: UserSubRepo):

        self._repo=repo


    async def add(self, task_id: int, user_id: int,message: SolCreate):
        ms={dt.name: getattr(message,dt.name) for dt in fields(message)}

        sub=SubPostAdd(task_id=task_id,user_id=user_id,code=message.code,message=ms)
        
       
        us=await self._repo.submis_add(sub)
        return us





        


 

        