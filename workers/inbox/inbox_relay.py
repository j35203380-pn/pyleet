from models import InboxSub,Submission
from db import AsyncLocal
from shemas import ExecutionResult,SubmissionUpdate
from faststream.rabbit import RabbitMessage,RabbitQueue,RabbitExchange,Channel,RabbitRouter
from faststream import AckPolicy
from uuid import UUID
from sqlalchemy import update,insert
import logging
from sqlalchemy.exc import IntegrityError
import msgspec


decoder=msgspec.json.Decoder(type=ExecutionResult)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

inboxrout=RabbitRouter()


EXCHANGE=RabbitExchange('submission')
QUEUE=RabbitQueue('solution.result')


@inboxrout.subscriber(queue=QUEUE,exchange=EXCHANGE,channel=Channel(prefetch_count=50),ack_policy=AckPolicy.NACK_ON_ERROR)
async def inbox_sub(msg: RabbitMessage):
    print('inbxostrater')
    logging.info('брокер inbox  взял запрос ')
    result=decoder.decode(msg.body)
    submission_id=UUID(msg.correlation_id)
    
    data=SubmissionUpdate(status=result.status,
                             exit_code=result.exit_code,
                             output=result.output,
                             time_ms=result.time_ms)
    try:

        async with AsyncLocal() as session:
            async with session.begin():
                event=await session.get(InboxSub,submission_id,with_for_update=True)
                if event:
                    return

                subdb=await session.execute(
                    update(Submission)
                    .where(Submission.id==submission_id)
                    .values(**msgspec.to_builtins(data))
                )
                if subdb.rowcount==0:
                    return
                
                evsub=dict(submission_id=submission_id,payload=msgspec.to_builtins(result))
                event=await session.execute(insert(InboxSub).values(**evsub))
        
     



    except IntegrityError:
        logging.error(f'конкурентная ставка')


        

   


