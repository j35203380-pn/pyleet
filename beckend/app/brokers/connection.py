from faststream.rabbit import RabbitBroker
from config import settings


#broker=RabbitBroker(settings.RABBIT_BROKER_URL)
broker=RabbitBroker(port=5673)