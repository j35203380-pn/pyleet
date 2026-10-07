from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


import asyncio



_semaphore=asyncio.Semaphore(20)


ph=PasswordHasher()

class CryptoAuth:

    @classmethod        
    def hash_password(cls,password: str):
        h=ph.hash(password)
        return h


    @classmethod
    def verify_password(cls, hash,password: str):
        try:
            ph.verify(hash,password)
            return True
        except VerifyMismatchError:
            return False
