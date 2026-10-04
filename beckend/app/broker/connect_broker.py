from faststream.rabbit import RabbitBroker
from config  import settings

broker=RabbitBroker(settings.RABBIT_BROKER_URL)