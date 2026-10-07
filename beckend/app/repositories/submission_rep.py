from app.repositories.base import BaseRepository
from sqlalchemy import insert
from app.database.models import Submission,OutboxSub
import asyncio
from app.schemas.solution import SubPostAdd


_semaphore=asyncio.Semaphore(20)



class UserSubRepo(BaseRepository):

    async def submis_add(self,users: SubPostAdd):
        
        async with _semaphore:
                
            async with self._db.begin():

                subdict=dict(user_id=users.user_id,task_id=users.task_id,code=users.code)
                submis=await self._db.execute(
                    insert(Submission)
                    .values(**subdict)
                    .returning(Submission)
                    )
                sub=submis.scalar_one_or_none()

                outbox=dict(submission_id=sub.id,message=users.message)
                await self._db.execute(
                    insert(OutboxSub)
                    .values(**outbox))
            return sub
            
            


