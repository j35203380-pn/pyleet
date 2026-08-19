from app.database.shemas.auth_shemas import (UserLogin,UserPost,
                                             ToeknPayload,Token,
                                             Bayer as BayerPost,
                                             Seller as SellerPost)
from app.database.db import get_db,AsyncSession
from fastapi import APIRouter,Depends,HTTPException,status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.database.models import User_auth as User,Seller,Buyer
from app.auth.auth import hashed,verifi,create_token,oauth_shemas
from sqlalchemy import select
from sqlalchemy.orm import joinedload


router=APIRouter(prefix='/auth')

GetDB=Annotated[AsyncSession,Depends(get_db)]

@router.post('/registr/bayer')
async def registration(user: BayerPost,db: GetDB):
    password_hesh=hashed(user.password)
    async with db.begin():
        new_us=User(name=user.name,nik_name=user.nik_name, 
                    role=user.role, email=user.email,
                    password=password_hesh,buyers=Buyer())
        db.add(new_us)
        return status.HTTP_201_CREATED



@router.post('/registr/seller')
async def Registration_sellers(user: SellerPost,db: GetDB):
    password_hesh=hashed(user.password)
    async with db.begin():
        new_us =User(
            name=user.name,nik_name=user.nik_name,
            role=user.role, email=user.email,
            password=password_hesh,
            sellers=Seller(inn=user.inn))
        db.add(new_us)
        return status.HTTP_201_CREATED









@router.post('/login',include_in_schema=True)
async def login(user: Annotated[OAuth2PasswordRequestForm,Depends()],
                db: AsyncSession=Depends(get_db)):
    user_=await db.execute(select(User).options(
                            joinedload(User.sellers),joinedload(User.buyers))
                           .where(User.nik_name == user.username))
    id=user_.unique().scalars().first()
    if not id:
        raise HTTPException (status_code=403,detail="Пользователь не найден")

    passwords=verifi(id.password, user.password)

    if not passwords:
        raise HTTPException (status_code=403,detail="неверный пароль")

    buyer_id=id.buyers.id if id.buyers else None
    seller_id=id.sellers.id if id.sellers else None
    token=create_token(user_id=id.id,role=id.role,
                       token_type= 'access',expires_delta=30,
                       seller_id=seller_id,buyer_id=buyer_id)
    if not token:
        raise HTTPException(status_code=404,detail='Пользователь не найден')    

    return {'access_token' : token, 'token_type': 'bearer'} 


@router.get('/me')
async def read_user_me(token :str= Depends(oauth_shemas)):

        return {'access_token' : token, 'token_type': 'bearer'} 
