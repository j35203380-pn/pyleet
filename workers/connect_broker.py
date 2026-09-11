from faststream.rabbit import RabbitBroker
from config import settings
from inbox.inbox_relay import inboxrout 


broker=RabbitBroker(settings.RABBIT_BROKER_URL)

broker.include_router(inboxrout)