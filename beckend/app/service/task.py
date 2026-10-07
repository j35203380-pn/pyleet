from app.database.db import AsyncLocal
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.repositories import TaskRepo
from app.exceptions import TaskNotFoundError

class TaskService:

    def __init__(self,repo: TaskRepo):

        self._repo=repo


    async def get_id(self, task_id: int):
        
        task=await self._repo.get_task(task_id=task_id)
        if not task:
             raise TaskNotFoundError()
        return task



        


 

        