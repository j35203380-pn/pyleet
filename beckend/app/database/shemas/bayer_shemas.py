from pydantic import BaseModel,ConfigDict,json
from datetime import datetime

class TaskBayerGet(BaseModel):
    id : int
    name : str
    text : str 
    comments : list[str] = [] #все коментарии/обсуждения к задаче
    
    model_config = ConfigDict(from_attributes=True)

class TaskBayerContinue(TaskBayerGet):
    proviso : str
       
    model_config = ConfigDict(from_attributes=True)

class TaskBayerSolutionGet(BaseModel):
    id : str
    content : json
    task : str
    creadet_at : datetime

    model_config= ConfigDict(from_attributes=True)

    


