from app.database.shemas.auth_shemas import UserPost
from fastapi import APIRouter,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.security import oauth_shemas
from app.auth.service import auth_service,UserAuthService

import logging

router=APIRouter(prefix='/auth',tags=["Авторизация и Вход"])

def services_auth():
    return auth_service

AuthServ=Annotated[UserAuthService,Depends(services_auth)]
UsReqForm=Annotated[OAuth2PasswordRequestForm,Depends()]


@router.post('/')
async def registration(user: UserPost,serv: AuthServ):
    logging.info('запрос отправлен')
    st=await serv.add_user(users=user)
    return st



@router.post('/login',include_in_schema=True)
async def login(user: UsReqForm,serv: AuthServ):

    token=await serv.get_user(username=user.username,password=user.password)
    return {'access_token' : token, 'token_type': 'bearer'} 



@router.get('/me')
async def read_user_me(token :str= Depends(oauth_shemas)):

        return {'access_token' : token, 'token_type': 'bearer'} 
