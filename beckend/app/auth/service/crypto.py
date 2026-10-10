from app.auth.security import CryptoAuth
from app.exceptions import InvalidPasswordException
import asyncio

class CryptoService:

    def __init__(self, crypt: CryptoAuth):
        self._crypt=crypt


    async def hash_password(self,password: str):

        return await asyncio.to_thread(
                        self._crypt._hash_,
                        password=password.encode())
        



    async def verify_password(self, hash: bytes,password: str):
        
        try:
            await asyncio.to_thread(
                        self._crypt._verify_,
                        hash,password.encode())
            return True
        except:
            raise InvalidPasswordException()
