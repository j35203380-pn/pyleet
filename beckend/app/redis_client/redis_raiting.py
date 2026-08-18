from redis.asyncio import Redis


class Raiting:

    def __init__(self,redis: Redis, 
                 prefix: str, 
                 timeout: float|int,
                 key: str|None=None):

        self._redis=redis
        self._prefix=prefix
        self._key=key
        self._time=timeout


    @property
    def prefix_key(self):
        if self._key:
            return f'{self._prefix}:{self._key}'
        return self._prefix

    @property
    def TimeOut(self):
        return 60*60*24*30 if not self._time else self._time


    async def post_raiting(self,enum_id: int):

        await self._redis.zincrby(self.prefix_key, 1, enum_id)

        await self._redis.expire(self.prefix_key,self.TimeOut, nx=True)


    async def get_raiting(self,maxs=10):

        return await self._redis.zrevrange(self.prefix_key,0,maxs-1)