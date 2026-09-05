from app.database.models import InboxSub,Submission
from app.database.db import AsyncLocal
from app.brokers import broker
from app.database.shemas.task_shemas import ExecutionResult,SubmissionUpdateADD
from faststream.rabbit import RabbitMessage,RabbitQueue,RabbitExchange,Channel
from faststream import AckPolicy
from uuid import UUID
from sqlalchemy import update,insert
from app.exceptions import SubmissionNOtFound
from app.routers.service import determine_statuse
import logging


EXCHANGE=RabbitExchange('submission')
QUEUE=RabbitQueue('solution.result')


@broker.subscriber(queue=QUEUE,exchange=EXCHANGE,channel=Channel(prefetch_count=50),ack_policy=AckPolicy.NACK_ON_ERROR)
async def inbox_sub(msg: RabbitMessage):
    result=ExecutionResult.model_validate_json(msg.body)
    submission_id=UUID(msg.correlation_id)
    status=determine_statuse(exit_code=result.exit_code)
    data=SubmissionUpdateADD(status=status,
                             exit_code=result.exit_code,
                             output=result.output,
                             time_ms=result.time_ms)
    try:

        async with AsyncLocal() as session:
            async with session.begin():
                event=await session.get(InboxSub,submission_id)
                if event:
                    return

                subdb=await session.execute(
                    update(Submission)
                    .where(Submission.id==submission_id)
                    .values(**data.model_dump())
                )
                if subdb.rowcount==0:
                    raise SubmissionNOtFound()
                
                evsub=dict(submission_id=submission_id,payload=result.model_dump())
                event=await session.execute(insert(InboxSub).values(**evsub))
        
     

    except SubmissionNOtFound as e:
        logging.error(e)
        

   


