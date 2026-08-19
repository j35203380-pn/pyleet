from pydantic import BaseModel,ConfigDict
from datetime import datetime



class ProvisoPost(BaseModel):
    text:str
    solution : str

    model_config=ConfigDict(from_attributes=True)

class TaskPost(BaseModel):
    name: str
    proviso: ProvisoPost
    

class ProvisoPatch(BaseModel):
    text: str|None=None
    solution: str|None=None

    model_config=ConfigDict(from_attributes=True)
    
class TaskPatch(BaseModel):
    name: str|None= None
    proviso:ProvisoPatch|None=None


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

    comment: str

    

class CommetnsGet(BaseModel):
    id : int
    buyer_id : int
    task_id : int
    comment: str
    created_at : datetime

    model_config= ConfigDict(from_attributes=True)