from config import settings
import jwt




class JWTUtils:
    
        
    @classmethod
    def encode(cls, payload):

        
        return jwt.encode(payload,
                        settings.SECRET_KEY,
                        algorithm=settings.ALGORITHM)
        


    
    
    @classmethod
    def decode(cls, token: str):

        return jwt.decode(token,
                          settings.PUBLIC_KEY,
                          algorithms=[settings.ALGORITHM])

    
        
        
        