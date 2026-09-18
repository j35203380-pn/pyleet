from app.database.db import AsyncLocal
from app.database.models import InboxSub,OutboxSub
from sqlalchemy import delete,or_
from datetime import datetime,timedelta
from faststream.rabbit import RabbitRouter

cl_broker=RabbitRouter()
QUEUE_CL='clear'
EXCHANGE_CL='outbox_inbox'

@cl_broker.subscriber(queue=QUEUE_CL,exchange=EXCHANGE_CL)
async def clear_outbox_inbox():
    print('функия клеар исполнятеся ')
    datat=datetime.utcnow() - timedelta(hours=24)
    async with AsyncLocal() as session:
        async with session.begin():
            await session.execute(
                delete(InboxSub)
                .where(InboxSub.processed_at<datat)
            )
            await session.execute(
                delete(OutboxSub)
                .where(or_(
                    OutboxSub.processed_at<datat,
                    OutboxSub.failed_at.is_not(None)
                    )
            ))


