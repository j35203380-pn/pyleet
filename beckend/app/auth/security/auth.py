from argon2 import PasswordHasher


ph=PasswordHasher()

class CryptoAuth:

    @classmethod        
    def _hash_(cls,password: bytes):
        return ph.hash(password)
        


    @classmethod
    def _verify_(cls, hash: bytes,password: bytes):
        
        return ph.verify(hash,password)
            
