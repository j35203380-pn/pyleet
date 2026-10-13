from fastapi import APIRouter
from app.database.shemas.auth_shemas import UserPost
from app.auth.dependcies.auth import AuthService
import logging



router=APIRouter()


@router.post('/regist')
async def registration(user: UserPost,serv: AuthService):
    logging.info('запрос отправлен')
    st=await serv.add_user(users=user)        
    return st





