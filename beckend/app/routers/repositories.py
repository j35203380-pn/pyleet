from app.database.db import AsyncSession
from pydantic import BaseModel
from sqlalchemy import insert,select
from app.database.models import Proviso,Task,User_auth as User,Seller
from app.database.shemas.task_shemas import TaskPost,ProvisoPost
from fastapi import status,HTTPException



class UserRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db


    async def post_task(self,tasks: TaskPost ,proviso: ProvisoPost,seller_id: int):

        async with self._db.begin():

            new_task=Task(
                name=tasks.name,
                seller_id=seller_id,
                proviso=Proviso(**proviso.model_dump())
            )

            self._db.add(new_task)
        return status.HTTP_201_CREATED

   