from app.database.shemas.auth_shemas import UserPost
from fastapi import APIRouter,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.security import oauth_shemas
from app.auth.service import auth_service



router=APIRouter(prefix='/auth',tags=["Авторизация и Вход"])


@router.post('/')
async def registration(user: UserPost):
   
    st=await auth_service.add_user(users=user)
    return st



@router.post('/login',include_in_schema=True)
async def login(user: Annotated[OAuth2PasswordRequestForm,Depends()]):

    token=await auth_service.get_user(user)
    return {'access_token' : token, 'token_type': 'bearer'} 



@router.get('/me')
async def read_user_me(token :str= Depends(oauth_shemas)):

        return {'access_token' : token, 'token_type': 'bearer'} 
