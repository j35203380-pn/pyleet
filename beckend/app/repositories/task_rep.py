from app.database.db import AsyncSession
from sqlalchemy import select
from app.exceptions import TaskNotFoundError                     
from app.database.models import Task
import asyncio
import logging


LimitDB=asyncio.Semaphore(20)



class TaskRepo:

    def __init__(self, db: AsyncSession):
        self._db=db



    async def get_task(self,task_id: int):
        logging.info("в процессе GetTask")

        async with LimitDB:
            async with self._db.begin():

                task=await self._db.get(Task,task_id)

               
        logging.info("GetTask успешно выполнен")
        return task





    async def level_task(self,level: str):

        async with LimitDB:
            task= await self._db.execute(
                select(Task.id,Task.title,Task.difficulty)
                .where(Task.difficulty == level)
            )
            t=task.all()
            if not t:
                raise TaskNotFoundError()

            return t