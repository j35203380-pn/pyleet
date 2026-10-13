from dataclasses import dataclass,field
import time
from uuid import UUID



@dataclass(slots=True)
class UserAuthAdd:
    name: str
    nik_name: str
    email: str
    password: str
    password_confim: str



@dataclass(slots=True)
class UserLoginGetDto:
    user_id: UUID |None=None
    nik_name: str|None=None
    passsword_hash: str|None=None
    is_error: bool=False
    is_totp_enable: bool = False




@dataclass(slots=True)
class UserTOTPDTO:
    user_id: UUID
    last_used: int=field(default_factory=lambda:int(time.time()/30))


    

