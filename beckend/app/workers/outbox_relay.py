from app.database.models import OutboxSub
from app.database.db import AsyncLocal
from app.brokers.connection import broker
from sqlalchemy import select,and_
from app.routers.repositories import UserSubRepositories
from faststream.rabbit import RabbitExchange,RabbitQueue
import asyncio
from datetime import datetime,timezone
import logging


MAX_RES=5
EXCHANGE=RabbitExchange('submission')
QUEUE=RabbitQueue('solution.execute')



async def outbox_res():
    while True:
        async with AsyncLocal() as session:
            async with session.begin():

                mesout= await session.execute(
                    select(OutboxSub)
                    .where(and_(
                                OutboxSub.processed_at.is_(None),
                                OutboxSub.failed_at.is_(None)
                                )
                            )
                    .limit(50)
                    .with_for_update(skip_locked=True)
                    )
                data=mesout.scalars().all()
                for sub in data:
                    message=sub.message
                    correlation_id=str(sub.submission_id)
                    try:
                        await broker.publish(message=message,
                                            queue=QUEUE,
                                            exchange=EXCHANGE,
                                            correlation_id=correlation_id,)
                    except Exception as ex:
                        logging.warning(f'не удалось опубликовать {sub.submission_id}: {ex}')
                        sub.last_error=str(ex)[:500]
                        sub.count+=1
                        if sub.count>MAX_RES:
                            sub.failed_at=datetime.now(timezone.utc)
                        
                        continue

                    sub.processed_at=datetime.now(timezone.utc)
        
        await asyncio.sleep(1)