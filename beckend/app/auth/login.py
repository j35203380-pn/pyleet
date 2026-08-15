from app.database.shemas.auth_shemas import UserLogin,UserPost,ToeknPayload,Token
from app.database.db import get_db,AsyncSession
from fastapi import APIRouter,Depends,HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.database.models.auth_models import User_auth as User
from app.auth.auth import hashed,verifi,create_token,oauth_shemas
from sqlalchemy import select


router=APIRouter(prefix='/auth')



@router.post('/registr')
async def registration(user: UserPost,db: AsyncSession=Depends(get_db)):
    password_hesh=hashed(user.password)
    async with db.begin():
        new_us=User(name=user.name,nik_name=user.nik_name, 
                    role=user.role, email=user.email,password=password_hesh)
        db.add(new_us)
        return {'status' : 200, "detail" : "Успешно"}



@router.post('/login',include_in_schema=True)
async def login(user: Annotated[OAuth2PasswordRequestForm,Depends()],
                db: AsyncSession=Depends(get_db)):
    user_=await db.execute(select(User).where(User.nik_name == user.username))
    id=user_.scalars().first()
    if not user_:
        raise HTTPException (status_code=403,detail="Пользователь не найден")

    passwords=verifi(id.password, user.password)
    if not passwords:
        raise HTTPException (status_code=403,detail="неверный пароль")

    token=create_token(user_id=id.id,role=id.role,token_type= 'access',expires_delta=30)
    if not token:
        raise HTTPException(status_code=404,detail='Пользователь не найден')    

    return {'access_token' : token, 'token_type': 'bearer'} 


@router.get('/me')
async def read_user_me(token :str= Depends(oauth_shemas)):

        return {'access_token' : token, 'token_type': 'bearer'} 
