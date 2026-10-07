from app.database.shemas.auth_shemas import UserPost
from app.database.db import get_db
from fastapi import APIRouter,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.dependcies.auth import services_auth,current_token
from app.auth.service.user import UserAuthService
from app.auth.repositories.repositories import AuthRepositories
import logging



router=APIRouter(prefix='/auth',tags=["Авторизация и Вход"])



AuthServ=Annotated[UserAuthService,Depends(services_auth)]
UsReqForm=Annotated[OAuth2PasswordRequestForm,Depends()]


@router.post('/')
async def registration(user: UserPost,serv: AuthServ):
    logging.info('запрос отправлен')
    st=await serv.add_user(users=user)        
    return st



@router.post('/login')
async def login(user: UsReqForm,serv: AuthServ):

    token=await serv.get_user(username=user.username,password=user.password)
    return {'access_token' : token, 'token_type': 'bearer'} 



