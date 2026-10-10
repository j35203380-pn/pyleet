from dataclasses import dataclass



@dataclass(slots=True)
class UserAuthAdd:
    name: str
    nik_name: str
    email: str
    password: str
    password_confim: str





