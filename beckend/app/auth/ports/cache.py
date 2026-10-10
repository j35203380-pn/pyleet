from redis.asyncio import Redis
from typing import Protocol


class Cache(Protocol):

    async def get(name: str):
        pass

    async def set(name: str, value: str|int|float, ex: int|float):
        pass