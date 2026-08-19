from app.database.shemas.task_shemas import (CommentsPost)
from fastapi import APIRouter,HTTPException,Depends,status
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.dependcies import ReschePoints
from typing import Annotated
from config import Role
from app.routers.repositories import UserRepositories 


#для проверки доступа 
is_sellers = ReschePoints(Role.SELLER,Role.BAYER)


routers = APIRouter(prefix='/coments',
                   dependencies=[Depends(is_sellers)])




def connect_db(db : AsyncSession= Depends(get_db)):
    return UserRepositories(db)


CurrenUser = Annotated[dict,Depends(current_token)]
PostDb = Annotated[UserRepositories,Depends(connect_db)]




@routers.post('/{task_id}',status_code=status.HTTP_201_CREATED)
async def add_comment(task_id: int, comments: CommentsPost,
                      user: CurrenUser, db:PostDb):

    await db.AddComments(comments=comments, user_id=user['id'], task_id=task_id)



