from pydantic import BaseModel,ConfigDict
from datetime import datetime
from config import SubmissionStatus
from uuid import UUID


class TaskCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    solution: str




class CommentsCreate(BaseModel):

    comment: str

    

class CommetnsGet(BaseModel):
    id : int
    user_id: int
    task_id: int
    comment: str
    created_at : datetime
    update_at : datetime


    model_config= ConfigDict(from_attributes=True)


class TaskDetailGet(BaseModel):
    id : int
    title : str 
    description: str
    difficulty: str
    starter_code: str
    method_name: str
    comments : int
    

    model_config = ConfigDict(from_attributes=True)


class TaskListItemGet(BaseModel):
    id: int
    title: str
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class SubmissionCreate(BaseModel):
    code: str


class SubmissionAccepted(BaseModel):
    id: int
    status: SubmissionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionListItemGet(BaseModel):
    id: int
    status: SubmissionStatus
    time_ms: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionUpdateADD(BaseModel):
    status: SubmissionStatus
    exit_code: str
    output: str
    time_ms: float


class ExecutionResult(BaseModel):
    logs: list[str]
    output: str
    exit_code: int
    test_result: list[dict]|None
    time_ms: float


class ExecutionRequest(BaseModel):
    mode: str
    code: str
    method_name: str
    test_cases: list[dict]

class CategoriesItemList(BaseModel):
    name: str
    tasks: list[TaskListItemGet]=[]

    model_config=ConfigDict(from_attributes=True)

class CategoryAllGet(BaseModel):
    id : int
    name: str

    model_config=ConfigDict(from_attributes=True)


class CategoryAllCreate(BaseModel):
    
    name: list[CategoryAllGet]

    model_config=ConfigDict(from_attributes=True)