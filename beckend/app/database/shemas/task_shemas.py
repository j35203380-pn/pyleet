from pydantic import BaseModel,ConfigDict
from datetime import datetime

class TaskPost(BaseModel):

    seller_id : int
    text : str 
    proviso_id : int

    


class ProvisoPost(BaseModel):
    solution : str

    

class ProvisoGet(BaseModel):
    id : int
    solution : str
    task : str

    model_config = ConfigDict(from_attributes=True)

class TaskGet(BaseModel):
    id : int
    seller_id : int
    text : str 
    proviso_id : int
    seller : str
    proviso : str
    solutions : list[str] = []
    comments : list[str]=[]
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)

class CommentsPost(BaseModel):

    buyer_id : int
    task_id : int
    comment: str

    

class CommetnsGet(BaseModel):
    id : int
    buyer_id : int
    task_id : int
    comment: str
    created_at : datetime

    model_config= ConfigDict(from_attributes=True)