from dataclasses import dataclass
from enum import Enum

@dataclass(slots=True)
class UserAuthAdd:
    name: str
    nik_name: str
    email: str
    password: str
    password_confim: str




