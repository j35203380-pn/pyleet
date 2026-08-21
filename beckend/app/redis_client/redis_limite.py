from redis.asyncio import Redis
from time import time
from random import randint
class RateLimite:

    def __init__(self, redis: Redis):
        self._redis=redis


    def cache_key(self,endpoint: str,ip_adress: str):
        return f"limite:{endpoint}:{ip_adress}"


    async def is_limite(self,endpoint: str,ip_adress: str,
                         max_request: int, window_second: int):
        ttl=int(time()*1000)
        key=self.cache_key(endpoint,ip_adress)
        member=f"{ttl}:{randint(0, 1_000_000_000)}"
        scoretime=ttl-(window_second*1000)

        async with self._redis.pipeline() as pipe:
            await pipe.zremrangebyscore(key, 0, scoretime)
            await pipe.zadd(key, mapping={member:ttl})
            await pipe.zcard(key)
            await pipe.expire(key,window_second)

            result=await pipe.execute()
        res=result[2]
        return res>=max_request    
