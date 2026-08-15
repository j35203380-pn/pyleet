from pydantic import BaseModel,EmailStr,field_validator,model_validator,ConfigDict
from app.database.models.auth_models import Rolename
from datetime import datetime


class UserPost(BaseModel):
    name : str
    nik_name : str
    role : Rolename
    email : EmailStr
    password : str
    password_confim : str


    @field_validator('nik_name')
    @classmethod
    def nikname_validation(cls,n):
        if not (n[0].isalpha() or n[0] != '_'):
            raise ValueError("Непраивльное имя пользователя")
        return n

    @field_validator('password')
    @classmethod
    def chekc_password(cls,v : str):
        if len(v)<8 :
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v

    @model_validator(mode='after')
    def password_models(self):
        if self.password != self.password_confim:
            raise ValueError("Пароли не совпадают")
    
        return self
    
    @field_validator('role')
    @classmethod
    def role_validation(cls,r):
        allow_roles={Rolename.seller,Rolename.buyer}
        if r not in allow_roles:
            raise ValueError("Ведены не существующие данные")
        return r

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class Token(BaseModel):
    acces_token : str
    token_type: str = 'bearer'

class ToeknPayload(BaseModel):
    sub : str
    role : str