from pydantic import BaseModel,EmailStr,field_validator,model_validator,ConfigDict,Field
from datetime import datetime


class UserPost(BaseModel):
    name : str
    nik_name : str
    email : EmailStr
    password : str=Field(min_length=8)
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
    
class UserAdd(BaseModel):
    name : str
    nik_name : str
    email : EmailStr
    password : str


class UserLogin(BaseModel):
    email : EmailStr
    password : str

class Token(BaseModel):
    access_token : str
    token_type: str = 'bearer'

class ToeknPayload(BaseModel):
    sub : str
    role : str