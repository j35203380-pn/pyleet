from redis.asyncio import Redis
from pydantic import BaseModel, TypeAdapter
from typing import Any
from random import randint
import json

class RedisCache:

    def __init__(self,redis: Redis,
                  prefix: str,
                  key: str | None =None,
                  ttl: int=30):

        self._redis=redis
        self._prefix=prefix
        self._key=key
        self._ttl=ttl



    def cache_key(self, enum_id: str| int, suffix: str|None=None):
        if suffix:
            if self._key:
                return f"{self._prefix}:{self._key}:{suffix}:{enum_id}"
            return f"{self._prefix}:{suffix}:{enum_id}"

        if self._key:
            return f"{self._prefix}:{self._key}:{enum_id}"

        return f"{self._prefix}:{enum_id}"


    @property
    def ttl_(self):
        return randint(self._ttl-3,self._ttl+3)



    async def set_cache(self, enum_id: str|int,
                         pow: BaseModel,suffix: str|None=None):
        if suffix:
            key= self.cache_key(enum_id,suffix)

        else:
            key= self.cache_key(enum_id)
        
        await self._redis.set(key,pow.model_dump_json(), ex=self.ttl_)



    async def set_cache_list(self, enum_id: str|int,
                         pow: list,model: type[BaseModel],suffix: str|None=None):
        if suffix:
            key= self.cache_key(enum_id,suffix)

        else:
            key= self.cache_key(enum_id)

        res=[model.model_validate(item).model_dump() for item in pow]
        
        await self._redis.set(key,json.dumps(res), ex=self.ttl_)



    async def get_cache(self, enum_id: str|int, 
                        model: type[BaseModel]|None=None,suffix: str|None=None):
        if suffix:
            key= self.cache_key(enum_id,suffix)
        else:
            key= self.cache_key(enum_id)
        cash = await self._redis.get(key)
        if cash:
            
            if model:
                return model.model_validate_json(cash)

            return TypeAdapter(Any).validate_json(cash)

        return None
    


    def lock_key(self, enum_id: str|int,suffix: str|None=None,
                 timeout_: int=3,sleep_: float=0.5):
        if suffix:
            if self._key: 
                key = f'lock_key:{self._prefix}:{self._key}:{suffix}:{enum_id}'
            else:
                key = f'lock_key:{self._prefix}:{suffix}:{enum_id}'
                        
        elif self._key: 
            key = f'lock_key:{self._prefix}:{self._key}:{enum_id}'
                
        else:
            key=f'lock_key:{self._prefix}:{enum_id}'
        
        return  self._redis.lock(key, timeout=timeout_,sleep=sleep_)


    async def cache_del(self, enum_id: str|int,suffix: str|None=None):
        if suffix:
            key= self.cache_key(enum_id,suffix)
        else:
            key= self.cache_key(enum_id)
        await self._redis.unlink(key)


    async def cache_del_prefix(self):
        'удаляет все кеши по  префиксу'

        cash_delet=[]

        async for cash in self._redis.scan_iter(
                        match=f'{self._prefix}:*',
                        count=500):

            cash_delet.append(cash)

            if len(cash_delet)>=500:
                await self._redis.unlink(*cash_delet)
                cash_delet.clear()

        if cash_delet:
            await self._redis.unlink(*cash_delet)

       
    async def cache_del_key(self):
        cash_delet=[]

        async for cash in self._redis.scan_iter(match=f'{self._prefix}:{self._key}:*',count=500):

            cash_delet.append(cash)

            if len(cash_delet)>=500:
                await self._redis.unlink(*cash_delet)
                cash_delet.clear()
        
        if cash_delet:
            await self._redis.unlink(*cash_delet)    