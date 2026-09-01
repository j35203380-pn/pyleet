from app.brokers.connection import broker
from faststream.rabbit import RabbitBroker,RabbitExchange,RabbitMessage,RabbitQueue



class RabBroker():
    def __init__(self,broker: RabbitBroker):
        self._broker=broker


    async def SolutionPublish(self,queue: str,exchange: str):
        exchange_dec=await self._broker.declare_exchange(exchange)
        queue_dec= await self._broker.declare_queue(queue)
        await queue_dec.bind(exchange=exchange_dec,routing_key=queue_dec.name)
        