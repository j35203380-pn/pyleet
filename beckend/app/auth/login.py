from app.database.shemas.auth_shemas import UserPost
from app.database.db import get_db,AsyncSession
from fastapi import APIRouter,Depends,status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth import oauth_shemas
from app.auth.repositories import AuthRepositories

async def connect_db(db: Annotated[AsyncSession,Depends(get_db)]):
    return AuthRepositories(db)


GetDB = Annotated[AuthRepositories,Depends(connect_db)]


router=APIRouter(prefix='/auth',tags=["Авторизация и Вход"])


@router.post('/')
async def registration(user: UserPost,db: GetDB):
   
    await db.UserAdd(users=user)
    return status.HTTP_201_CREATED



@router.post('/login',include_in_schema=True)
async def login(user: Annotated[OAuth2PasswordRequestForm,Depends()],db: GetDB):

    token=await db.UserLogin(user)
    return {'access_token' : token, 'token_type': 'bearer'} 



@router.get('/me')
async def read_user_me(token :str= Depends(oauth_shemas)):

        return {'access_token' : token, 'token_type': 'bearer'} 
