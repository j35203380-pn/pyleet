from pydantic import BaseModel,ConfigDict,Field
from datetime import datetime
from config import SubmissionStatus
from uuid import UUID



class CommentsCreate(BaseModel):

    comment: str

    
class CommentUserGet(BaseModel):
    id: int
    name: str

class CommetnsGet(BaseModel):
    id : int
    comment: str
    created_at : datetime
    user: CommentUserGet=Field(validation_alias='users')

    model_config= ConfigDict(from_attributes=True)


class TaskDetailGet(BaseModel):
    id : int
    title : str 
    description: str
    difficulty: str
    starter_code: str
    method_name: str
    comments_count : int
    
    

    model_config = ConfigDict(from_attributes=True)



class TaskDetailGetAll(TaskDetailGet):
    solution: str
    test_cases: list[dict]

    model_config=ConfigDict(from_attributes=True)

class TaskListItemGet(BaseModel):
    id: int
    title: str
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class SubmissionCreate(BaseModel):
    code: str


class SubmissionAccepted(BaseModel):
    id: UUID
    status: SubmissionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionListItemGet(BaseModel):
    id: UUID
    status: SubmissionStatus
    time_ms: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionUpdateADD(BaseModel):
    status: SubmissionStatus
    exit_code: int
    output: str
    time_ms: float


class ExecutionResult(BaseModel):
    logs: list[str]
    output: str
    exit_code: int
    test_result: list[dict]|None=None
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