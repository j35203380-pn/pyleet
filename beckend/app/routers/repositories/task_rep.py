from app.database.db import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload,selectinload
from app.exceptions import TaskNotFoundError                     
from app.database.models import Task,Category,Comments
import asyncio
from config import DifficultyLevel


LimitDB=asyncio.Semaphore(20)



class TaskRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db



    async def GetTask(self,task_id: int):

        async with LimitDB:
            task=await self._db.get(Task,task_id)

        if not task:
            raise TaskNotFoundError()

        return task





    async def LevelTask(self,level: str):

        async with LimitDB:
            task= await self._db.execute(
                select(Task.id,Task.title,Task.difficulty)
                .where(Task.difficulty == level)
            )
            t=task.scalar_one_or_none()
            if not t:
                raise TaskNotFoundError()

            return t