from app.database.shemas.task_shemas import (CommentsPost)
from fastapi import APIRouter,HTTPException,Depends,status
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.dependcies import ReschePoints
from typing import Annotated
from config import Role
from app.routers.repositories import UserRepositories 


#для проверки доступа 
is_roles = ReschePoints(Role.SELLER,Role.BAYER)


routers = APIRouter(prefix='/coments',
                    tags=["Комменты"],
                    dependencies=[Depends(is_roles)])




def connect_db(db : AsyncSession= Depends(get_db)):
    return UserRepositories(db)


CurrenUser = Annotated[dict,Depends(current_token)]
PostDb = Annotated[UserRepositories,Depends(connect_db)]




@routers.post('/task/{task_id}',status_code=status.HTTP_201_CREATED)
async def add_comment(task_id: int, comments: CommentsPost,
                      user: CurrenUser, db:PostDb):

    return await db.AddComments(comments=comments, user_id=user['id'], task_id=task_id)




@routers.put('/task/{task_id}')
async def put_comments(task_id: int, comment_id: int, users: CurrenUser,
                            db: PostDb,comments: CommentsPost):

    return await db.UpdateComments(commetns_id=comment_id,task_id=task_id,
                                   user_id=users['id'],comments=comments)   



@routers.delete('/task/{task_id}')
async def delete_comments(task_id: int,comment_id: int, users: CurrenUser,db: PostDb):

    return await db.DelComments(task_id=task_id,comments_id=comment_id,user_id=users['id'])
