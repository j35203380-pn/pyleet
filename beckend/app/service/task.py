from app.database.db import AsyncLocal
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.repositories import TaskRepo
from app.exceptions import TaskNotFoundError

class TaskService:

    def __init__(self,async_maker: async_sessionmaker,repo: TaskRepo):
        self._maker=async_maker
        self._db=repo


    async def get_id(self, task_id: int):
        
        async with self._maker() as session:
                repo: TaskRepo=self._db(session)
                task=await repo.get_task(task_id=task_id)
        if not task:
             raise TaskNotFoundError()
        return task



task_serv=TaskService(AsyncLocal,TaskRepo)

        


 

        