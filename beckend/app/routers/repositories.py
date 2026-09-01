from app.database.db import AsyncSession
from sqlalchemy import insert,select,and_,update,delete,or_
from sqlalchemy.orm import joinedload
from app.database.shemas.task_shemas import (CommentsCreate,SubmissionCreate,
                                            SubmissionUpdateADD,ExecutionResult)
from app.database.shemas.auth_shemas import UserAdd,UserPost
from fastapi import status
from app.exceptions import (TaskNotFoundError,InvalidPasswordException,
                            UserNotFound,CommentNotFound,SubmissionNOtFound)
from app.database.models import Submission,Task,Comments,User
from app.auth.auth import PasswordHashed,PasswordVerifi,create_token
from fastapi.security import OAuth2PasswordRequestForm
from config import SubmissionStatus 
import asyncio
from uuid import UUID

LimitDB=asyncio.Semaphore(20)



class UserRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db



    async def UserAdd(self,users: UserPost):
        
        password_hash=PasswordHashed(users.password)
        users.password=password_hash
        us=dict(
            name=users.name,nik_name=users.nik_name,
            email=users.email,password=password_hash
        )
        await self._db.execute(
            insert(User)
            .values(**us)
        )
        return status.HTTP_201_CREATED


    async def UserLogin(self,users: OAuth2PasswordRequestForm):
        us=await self._db.execute(
            select(User)
            .where(or_
                   (User.nik_name==users.username,
                    User.email==users.username)))
        user=us.scalars().first()
        if not user:
            raise UserNotFound()
        password=PasswordVerifi(user.password,users.password)
        if not password:
            raise InvalidPasswordException()
        token= create_token(user_id=user.id,token_type= 'access',expires_delta=30)
        if not token:
            raise UserNotFound()
        return token



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
            
            comm=com.scalars().first()
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
            c=comm.scalars().first()
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
            if not comm:
                raise CommentNotFound()

            comment=comm.scalars().first()
        return comment
    

    async def AllGetComment(self,user_id: int, limit: int=20, offset: int=0):
        async with LimitDB:

            comm= await self._db.execute(
                select(Comments)
                .where(Comments.user_id==user_id)
                .order_by(Comments.created_at.desc())
                .limit(limit).offset(offset)
            )
            if not comm:
                raise CommentNotFound()

            comments=comm.scalars().all()

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



    async def SubmissionPost(self,task_id: int, user_id: int,submission: SubmissionCreate):
                                                                  
        subdict=dict(
            user_id=user_id,task_id=task_id,code=submission.code
        )
        submis=await self._db.execute(
            insert(Submission)
            .values(**subdict)
            .returning(Submission)
        )
        result=submis.scalars().first()
        if not result:
            raise SubmissionNOtFound()
        return result


    async def GetTask(self,task_id: int):

        async with LimitDB:
            task=await self._db.get(Task,task_id)
        if not task:
            raise TaskNotFoundError()

        return task


    async def SubmissionUpdate(self,submission_id: UUID,user_id: int,statuse: str,tasks: ExecutionResult):
        sub=SubmissionUpdateADD(
            status=statuse,
            exit_code=tasks.exit_code,
            output=tasks.output,
            time_ms=tasks.time_ms
        )

        
        async with LimitDB:
            res = await self._db.execute(
                        update(Submission)
                        .where(and_(
                             Submission.id==submission_id,
                             Submission.user_id==user_id))
                        .values(**sub.model_dump())
                        .returning(Submission)
                        )
            sub=res.scalars().first()
            if not sub:
                raise SubmissionNOtFound()
            
        return sub