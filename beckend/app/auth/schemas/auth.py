from dataclasses import dataclass
from enum import Enum
from typing import Literal


class TokenTypeEN(str,Enum):
    ACCESS='access'
    REFRESH='refresh'



@dataclass(slots=True)
class PayloadDTO:
    user_id: int
    nik_name: str
    token_type: Literal[TokenTypeEN.ACCESS,TokenTypeEN.REFRESH]






@dataclass(slots=True)
class ExpireJwtDTO:
    access_exp: int
    refresh_exp: int





class JWTPayloadEN(str,Enum):
    JTI='jti'
    TYPE='type'
    SUB='sub'
    EXP='exp'
    NAME='name'


class BlackLstMethod(str,Enum):
    ADD='add'
    GET='get'