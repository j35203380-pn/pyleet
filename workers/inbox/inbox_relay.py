from models import InboxSub,Submission
from db import AsyncLocal
from shemas import ExecutionResult,SubmissionUpdate
from faststream.rabbit import RabbitMessage,RabbitQueue,RabbitExchange,Channel,RabbitRouter
from faststream import AckPolicy
from uuid import UUID
from sqlalchemy import update,insert,select
import logging
from sqlalchemy.exc import IntegrityError
import msgspec
import asyncio

decoder=msgspec.json.Decoder(type=ExecutionResult)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

inboxrout=RabbitRouter()


EXCHANGE=RabbitExchange('submission')
QUEUE=RabbitQueue('solution.result')
queue_work=asyncio.Queue(40)


async def inbox_put(batch: list):
    sub_id=[data.submission_id for _,data,_ in batch]
    try:

        async with AsyncLocal() as session:
            async with session.begin():
                event=(await session.execute(
                    select(InboxSub.submission_id)
                    .where(InboxSub.submission_id.in_(sub_id))
                )).scalars().all()
                lock_events=set(event)
                _items=[]
                for msg,data,result in batch:
                    if data.submission_id in lock_events:
                        await msg.ack()
                    else:
                        _items.append([msg,data,result])

                sub_batch_id=[data.submission_id for _,data,_ in _items ]
                

                subdb=(await session.execute(
                    select(Submission)
                    .where(Submission.id.in_(sub_batch_id))
                    )).scalars().all()
                _subdb={s.id for s in subdb}
                _submission=[]
                _inbox=[]
                _msg=[]
                for msg,data,result in _items:
                    if data.submission_id in _subdb:
                        s=dict(**msgspec.to_builtins(data))
                        _id=s.pop('submission_id')
                        _submission.append(dict(id=_id,**s))
                        _inbox.append(dict(submission_id=data.submission_id,payload=msgspec.to_builtins(result)))
                        _msg.append(msg)
                                 
                if _submission:
                    sub=await session.execute(update(Submission),_submission)
                    event=await session.execute(insert(InboxSub),_inbox)
        
                for msg in _msg:
                    await msg.ack()




    except IntegrityError:
        logging.error(f'конкурентная ставка')





async def inbox_workers(queue: asyncio.Queue,timeout: int=1,max_len:int=40):
    print('inbox workers начал работу')
    batch=[]
    try:
        while True:
            try:

                task=await queue.get()
                batch.append(task)

                while len(batch)<=max_len:
                    print('inbox workers взялся за работу')
                    t=await asyncio.wait_for(queue.get(),timeout=timeout)
                    batch.append(t)

            except asyncio.TimeoutError:
                pass

            if batch:
                await inbox_put(batch)
                batch=[]
                print('сохранил данные в бд')
    except asyncio.CancelledError:
        if batch:
            await inbox_put(batch)
        raise




@inboxrout.subscriber(queue=QUEUE,exchange=EXCHANGE,channel=Channel(prefetch_count=50),ack_policy=AckPolicy.NACK_ON_ERROR)
async def inbox_sub(msg: RabbitMessage):
    print('inbxostrater')
    logging.info('брокер inbox  взял запрос ')
    result=decoder.decode(msg.body)
    submission_id=UUID(msg.correlation_id)
    
    data=SubmissionUpdate(status=result.status,
                          submission_id=submission_id,
                             exit_code=result.exit_code,
                             output=result.output,
                             time_ms=result.time_ms)

    await queue_work.put([msg,data,result])
        

   


