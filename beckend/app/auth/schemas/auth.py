from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class TokenTypeEN(StrEnum):
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





class PayloadSetEN(StrEnum):
    JTI='jti'
    TYPE='type'
    SUB='sub'
    EXP='exp'
    NAME='name'



class PayloadGetEN(StrEnum):
    ID='id'
    TYPE='type'
    NIK_NAME='nik_name'
    JTI='jti'
    EXP='exp'


                
class BlackLstMethod(StrEnum):
    ADD='add'
    GET='get'


