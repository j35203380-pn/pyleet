from redis.asyncio import Redis
from app.auth.schemas.token import TokenCacheDTO
from uuid import UUID
import orjson,time



class TokenService:
    def __init__(self,cache: Redis):
        self._redis=cache

    

    
    def _key_(self,token_hash: bytes):
        return f'{token_hash.hex()}'


        

    async def get_tokens(self,token_hash: bytes):
        try:
            key=self._key_(token_hash)
            token=await self._redis.get(key)
            if not token:
                return None

            data=orjson.loads(token)
            if int(time.time()/30)<=data['last_used']:
                return 'VZLOM'
            
            return data
        
        except Exception as e:
            raise RuntimeError(f"ошибка {e} редис не работает")
            
    
    async def set_token(self, token_hash: bytes, refresh: TokenCacheDTO):
        
        try:
            raw=orjson.dumps(token=refresh)
            key=self._key_(token_hash)
            ttl=refresh.expire_at
            await self._redis.set(key,raw,ttl)
        
        except Exception as e:
            raise RuntimeError(f"ошибка {e} редис не работает")


    async def del_token(self,token_hash: bytes):
        try:
            key=self._key_(token_hash)
            await self._redis.unlink(key)
        except Exception as e:
            raise RuntimeError(f"ошибка {e} редис не работает")
