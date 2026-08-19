from app.database.db import AsyncSession
from pydantic import BaseModel
from sqlalchemy import insert,select,and_,update,delete
from sqlalchemy.orm import joinedload
from app.database.shemas.task_shemas import TaskPost,CommentsPost,ProvisoPost,TaskPatch
from fastapi import status,HTTPException
from app.exceptions import TaskNotFoundError
from app.database.models import (Proviso,Task,User_auth as User,Seller,Comments)



class UserRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db


    async def PostTask(self,tasks: TaskPost, seller_id: int):

        async with self._db.begin():
            new_task=Task(
                name=tasks.name,
                seller_id=seller_id,
                proviso=Proviso(**tasks.proviso.model_dump())
                )

            self._db.add(new_task)
        return status.HTTP_201_CREATED


    async def AddComments(self, comments: CommentsPost, 
                          user_id: int, task_id: int):

        async with self._db.begin():
            new=dict(user_id=user_id,
                         task_id=task_id,
                         comment=comments.comment
                        )

            com=await self._db.execute(
                insert(Comments)
                .values(**new).returning(Comments))
            
            comm=com.scalars().first()
        return comm



    async def UpdateTask(self, task_id, 
                         seller_id,task: TaskPost|TaskPatch):

        update_name=task.model_dump(exclude_unset=True)
        async with self._db.begin():
            new=await self._db.execute(
                        select(Task).options(joinedload(Task.proviso))
                        .where(and_(
                                Task.id==task_id,seller_id==seller_id
                        ))
            )
            t=new.scalars().first()

            if not t:
                raise TaskNotFoundError()
            
            if 'name' in update_name:
                t.name=task.name

            if proviso_update:=update_name.get('proviso',None):
                
                for name,x in proviso_update.items():
                    if hasattr(t.proviso,name):
                        setattr(t.proviso,name,x)

        return t



    async def DeleteTask(self,task_id: int,seller_id: int):

        async with self._db.begin():
            row=await self._db.execute(
                delete(Task)
                .where(and_(
                    Task.id==task_id,Task.seller_id==seller_id)
                ))
        if row.rowcount == 0:
            raise TaskNotFoundError()
        return status.HTTP_200_OK
        

    

