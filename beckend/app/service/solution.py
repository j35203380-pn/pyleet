from app.database.db import AsyncLocal
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.repositories import UserSubRepo
from app.schemas.solution import SolCreate,SubPostAdd
from dataclasses import fields


class SolutionService:

    def __init__(self,async_maker: async_sessionmaker,repo: UserSubRepo):
        self._maker=async_maker
        self._db=repo


    async def add(self, task_id: int, user_id: int,message: SolCreate):
        ms={dt.name: getattr(message,dt.name) for dt in fields(message)}

        sub=SubPostAdd(task_id=task_id,user_id=user_id,code=message.code,message=ms)
        
        async with self._maker() as session:
                repo: UserSubRepo=self._db(session)
                us=await repo.submis_add(sub)
        return us



sol_service=SolutionService(AsyncLocal,UserSubRepo)

        


 

        