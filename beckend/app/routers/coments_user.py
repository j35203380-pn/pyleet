from app.database.shemas.task_shemas import CommentsCreate,CommetnsGet
from fastapi import APIRouter,HTTPException,Depends,status
from app.database.db import AsyncSession,get_db
from app.auth.auth import current_token
from app.dependcies import ReschePoints
from typing import Annotated

from app.routers.repositories import CommRepositories 



routers = APIRouter(prefix='/coments',
                    tags=["Комменты"],
                    dependencies=[Depends(current_token)])




def connect_db(db : AsyncSession= Depends(get_db)):
    return CommRepositories(db)


CurrenUser = Annotated[dict,Depends(current_token)]
PostDb = Annotated[CommRepositories,Depends(connect_db)]



@routers.get('/{task_id}',response_model=CommetnsGet)
async def get_commetns(task_id: int,user: CurrenUser, db: PostDb):
    return await db.GetComment(task_id=task_id,user_id=user['id'])




@routers.get('/user/all',response_model=list[CommetnsGet])
async def get_all_commetns(user: CurrenUser, db: PostDb,
                           limit: int=10,offset: int=0):
    return await db.AllGetComment(user['id'],limit=limit,offset=offset)




@routers.get('/task/{task_id}',response_model=list[CommetnsGet])
async def get_all_comments_task(task_id: int, db: PostDb, 
                                limit: int=10,offset: int=0):
    return await db.TaskComments(task_id=task_id,limit=limit,offset=offset)




@routers.post('/task/{task_id}',status_code=status.HTTP_201_CREATED)
async def add_comment(task_id: int, comments: CommentsCreate,
                      user: CurrenUser, db:PostDb):

    return await db.AddComments(comments=comments, user_id=user['id'], task_id=task_id)




@routers.put('/task/{task_id}')
async def put_comments(task_id: int, comment_id: int, users: CurrenUser,
                            db: PostDb,comments: CommentsCreate):

    return await db.UpdateComments(commetns_id=comment_id,task_id=task_id,
                                   user_id=users['id'],comments=comments)   



@routers.delete('/task/{task_id}')
async def delete_comments(task_id: int,comment_id: int, users: CurrenUser,db: PostDb):

    return await db.DelComments(task_id=task_id,comments_id=comment_id,user_id=users['id'])
