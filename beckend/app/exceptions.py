from fastapi import HTTPException

class AllExceptions(HTTPException):

    def __init__(self, status_code, detail = None, headers = None):
        super().__init__(status_code, detail, headers)

class TaskNotFoundError(AllExceptions):
    def __init__(self ):
        super().__init__(status_code=404, detail='Задача не найдена или недоступна для данного продавца')