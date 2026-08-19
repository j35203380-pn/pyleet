from pydantic import BaseModel,ConfigDict
from datetime import datetime



  

    

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
    solutions : str
    comments : str
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)


    
