from dataclasses import dataclass, field
from uuid import UUID
from app.auth.settings.base import expire
from app.auth.settings.base import expire
import time





@dataclass(slots=True)
class SessionAddDTO:
    user_id: UUID
    token_hash: bytes
    user_agent: str|None
    ip_adress: str|None 
    abs_expire: int=field(default_factory=lambda: int(time.time()+expire.refresh_exp))





@dataclass(slots=True)
class TokenCacheDTO:
    
    last_used: int=field(default_factory=lambda:int(time.time()/30))
    expire_at: int=field(default_factory=lambda: int(time.time()+expire.refresh_exp))



@dataclass(slots=True)
class SessionUpdDTO:
    token_hash: bytes
    ip_adress: str
    user_agent: str
