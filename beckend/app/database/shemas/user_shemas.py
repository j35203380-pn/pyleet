from pydantic import BaseModel,ConfigDict


class CommentsAllCreat(BaseModel):

    task_id : int
    comment : str

