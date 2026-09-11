from app.database.db import AsyncSession
from sqlalchemy import insert,and_,update
from app.database.shemas.task_shemas import SubmissionCreate,SubmissionUpdateADD,ExecutionResult,ExecutionRequest
from app.exceptions import SubmissionNOtFound
from app.database.models import Submission,OutboxSub
import asyncio
from uuid import UUID
from app.routers.repositories.shemas import ExecutionReq
import msgspec

_semaphore=asyncio.Semaphore(20)



class UserSubRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db



    async def SubmissionPost(self,task_id: int, user_id: int,message: ExecutionReq):
        payload=msgspec.to_builtins(message)
        async with _semaphore:
                
            async with self._db.begin():

                subdict=dict(user_id=user_id,task_id=task_id,code=message.code)
                submis=await self._db.execute(
                    insert(Submission)
                    .values(**subdict)
                    .returning(Submission)
                    )
                sub=submis.scalar_one_or_none()

                outbox=dict(submission_id=sub.id,message=payload)
                await self._db.execute(
                    insert(OutboxSub)
                    .values(**outbox))
            return sub
            
            


