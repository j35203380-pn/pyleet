from app.database.db import AsyncSession
from sqlalchemy import insert,and_,update
from app.database.shemas.task_shemas import SubmissionCreate,SubmissionUpdateADD,ExecutionResult
from app.exceptions import SubmissionNOtFound
from app.database.models import Submission
import asyncio
from uuid import UUID



LimitDB=asyncio.Semaphore(20)



class UserSubRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db



    async def SubmissionPost(self,task_id: int, user_id: int,submission: SubmissionCreate):
        
        async with self._db.begin():

            subdict=dict(
                user_id=user_id,task_id=task_id,code=submission.code
            )
            submis=await self._db.execute(
                insert(Submission)
                .values(**subdict)
                .returning(Submission)
            )
            result=submis.scalar_one_or_none()
            if not result:
                raise SubmissionNOtFound()
        return result




    async def SubmissionUpdate(self,submission_id: UUID,user_id: int,statuse: str,tasks: ExecutionResult):
        sub=SubmissionUpdateADD(
            status=statuse,
            exit_code=tasks.exit_code,
            output=tasks.output,
            time_ms=tasks.time_ms
        )

        
        async with LimitDB:
            async with self._db.begin():

                res = await self._db.execute(
                            update(Submission)
                            .where(and_(
                                Submission.id==submission_id,
                                Submission.user_id==user_id))
                            .values(**sub.model_dump())
                            .returning(Submission)
                            )
                sub=res.scalar_one_or_none()
                if not sub:
                    raise SubmissionNOtFound()
            
        return sub