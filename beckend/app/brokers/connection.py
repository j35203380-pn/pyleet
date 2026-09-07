from faststream.rabbit import RabbitBroker
from config import settings
from app.workers.inbox_relay import inboxrout

#broker=RabbitBroker(settings.RABBIT_BROKER_URL)
broker=RabbitBroker(port=5673)
broker.include_router(inboxrout)

