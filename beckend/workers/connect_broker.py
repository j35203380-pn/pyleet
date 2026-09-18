from faststream.rabbit import RabbitBroker
from config import settings
from workers.inbox.inbox_relay import inboxrout 
from workers.clear_db import cl_broker


broker=RabbitBroker(settings.RABBIT_BROKER_URL)

broker.include_router(inboxrout)
broker.include_router(cl_broker)




