import jwt


class JWTUtils:
    

    @classmethod
    def encode(cls, payload,private_key: bytes,algorithm: str):

        
        return jwt.encode(payload,
                        private_key,
                        algorithm=algorithm)
        


    @classmethod
    def decode(cls, token: str, public_key: bytes, algorithm: str):

        return jwt.decode(token,
                          public_key,
                          algorithms=[algorithm])

    
        
        
        