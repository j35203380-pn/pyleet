from models import OutboxSub
from db import AsyncLocal
from sqlalchemy import select,and_
from faststream.rabbit import RabbitExchange,RabbitQueue
import asyncio
from faststream.rabbit import RabbitRouter,RabbitPublisher
from datetime import datetime,timezone
import logging
from dataclasses import dataclass
from time import time
from connect_broker import broker

logger = logging.getLogger(__name__)

# --- tuning knobs ------------------------------------------------------
MAX_RETRIES = 5              # attempts before we give up on a submission
MAX_BACKOFF_SEC = 60          # ceiling for exponential backoff
BATCH_SIZE = 200              # rows claimed per DB round trip
PUBLISH_CONCURRENCY = 50      # лимит семафон
PUBLISH_TIMEOUT_SEC = 10    # a single publish must finish or die within this
IDLE_SLEEP_SEC = 1.0          # ждем если бд пусто
ERROR_SLEEP_SEC = 2.0         # sleep after an unexpected loop-level error

EXCHANGE = RabbitExchange("submission")
QUEUE = RabbitQueue("solution.execute")



@dataclass(slots=True)
class ClaimedItem:
    submission_id: str
    message: bytes | str
    count: int

_semaphone=asyncio.Semaphore(PUBLISH_CONCURRENCY)

def _is_ready(sub: OutboxSub,now: datetime):
    if sub.count==0:
        return True
    backoff=min(2**sub.count,MAX_BACKOFF_SEC)
    return (now-sub.last_attempt_at).total_seconds() >=backoff



async def run_broker(sub: OutboxSub):
    logging.info("broker взял данные")
    now=datetime.now(timezone.utc)
    async with _semaphone:
        try:
            logging.info('данные переданы через броке outbox relay')
            await asyncio.wait_for(
                    broker.publish(
                        message=sub.message,
                        queue=QUEUE,
                        exchange=EXCHANGE,
                        correlation_id=str(sub.submission_id),
                    ),
                    timeout=PUBLISH_TIMEOUT_SEC
                )
        except Exception as ex:
            logging.error('не удалось передать даннеы через outbox relay')
            sub.count+=1
            sub.last_error=str(ex)[:500]
            if sub.count>MAX_RETRIES:
                sub.failed_at=now
            return
        sub.processed_at=now







async def outbox_run():
    logging.info(" в outbox идем в бд")
    while True:
        async with AsyncLocal() as session:
            logging.info('открыли сессию')
            async with session.begin():
                logging.info('запрос в бд')
                data=(await session.execute(
                    select(OutboxSub)
                    .where(and_(
                        OutboxSub.failed_at.is_(None),
                        OutboxSub.processed_at.is_(None)
                    ))
                    .order_by(OutboxSub.created_at)
                    .limit(20)
                    .with_for_update(skip_locked=True)
                    )).scalars().all()
                if not data:
                    logging.info('бд пусто')
                logging.info('outbox relayвзял данные из бд')
                tm=len(data)==20
                now=datetime.now(timezone.utc)
                t2=time()
                async with asyncio.TaskGroup() as ts:
                    for sub in data:
                        logging.info('Outbox передае в брокеp')
                        if _is_ready(sub,now):
                            sub.last_attempt_at=now
                            task=ts.create_task(run_broker(sub))
           
        if not tm:
            await asyncio.sleep(5)
        else :
            await asyncio.sleep(0.2)
                
            