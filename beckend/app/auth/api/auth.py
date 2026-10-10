from app.database.shemas.auth_shemas import UserPost
from fastapi import APIRouter
from app.auth.dependcies.auth import AuthServ
import logging



router=APIRouter()


@router.post('/regist')
async def registration(user: UserPost,serv: AuthServ):
    logging.info('запрос отправлен')
    st=await serv.add_user(users=user)        
    return st




