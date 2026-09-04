from app.database.db import AsyncSession
from sqlalchemy import insert,select,and_,update,delete
from app.database.shemas.task_shemas import CommentsCreate
from fastapi import status
from app.exceptions import TaskNotFoundError,CommentNotFound
from app.database.models import Comments
import asyncio


LimitDB=asyncio.Semaphore(20)



class CommRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db




    async def AddComments(self, comments: CommentsCreate, 
                          user_id: int, task_id: int):

        async with self._db.begin():
            new=dict(user_id=user_id,
                         task_id=task_id,
                         comment=comments.comment
                        )

            com=await self._db.execute(
                insert(Comments)
                .values(**new).returning(Comments))
            
            comm=com.scalar_one_or_none()
        return comm


        

    
    async def UpdateComments(self,comments_id,task_id: int,user_id,comments: CommentsCreate):

        async with self._db.begin():
            comm=await self._db.execute(
                update(Comments)
                .where(and_(
                    Comments.id==comments_id,
                    Comments.user_id==user_id,
                    Comments.task_id==task_id))
                .values(comments.model_dump())
                .returning(Comments)
            )
            c=comm.scalar_one_or_none()
        return c






    async def DelComments(self,comments_id: int, task_id: int, user_id: int):

        async with self._db.begin():
            row=await self._db.execute(
                delete(Comments)
                .where(and_(
                    Comments.id==comments_id,
                    Comments.user_id==user_id,
                    Comments.task_id==task_id)))
            
            if row.rowcount == 0:
                raise TaskNotFoundError()
        return status.HTTP_200_OK






    async def GetComment(self,task_id: int,user_id : int):
        
        async with LimitDB:

            comm=await self._db.execute(
                select(Comments)
                .where(and_(
                    Comments.task_id==task_id,Comments.user_id==user_id
                ))
            )
            print(comm)
            comment=comm.scalars().all()
            
            if not comment:
                raise CommentNotFound()

        return comment
    





    async def AllGetComment(self,user_id: int, limit: int=20, offset: int=0):
        
        async with LimitDB:

            comm= await self._db.execute(
                select(Comments)
                .where(Comments.user_id==user_id)
                .order_by(Comments.created_at.desc())
                .limit(limit).offset(offset)
            )
            comments=comm.scalars().all()
            
            if not comments:
                raise CommentNotFound()


        return comments






    async def TaskComments(self,task_id: int, limit: int=20, offset: int=0):
        async with LimitDB:
            comm= await self._db.execute(
                select(Comments)
                .where(Comments.task_id==task_id)
                .order_by(Comments.created_at.desc())
                .limit(limit).offset(offset)
            )
            if not comm:
                raise CommentNotFound()

            comments=comm.scalars().all()

        return comments





