from fastapi import HTTPException

class AllExceptions(HTTPException):

    def __init__(self, status_code, detail = None, headers = None):
        super().__init__(status_code, detail, headers)

class TaskNotFoundError(AllExceptions):
    def __init__(self):
        super().__init__(status_code=404, detail='Задача не найдена')

class InvalidPasswordException(AllExceptions):
    def __init__(self):
        super().__init__(status_code=401, detail='Неправильно веден пароль',)

class UserNotFound(AllExceptions):
    def __init__(self):
        super().__init__(status_code=401, detail='Пользователь не найден')

class CommentNotFound(AllExceptions):
    def __init__(self):
        super().__init__(status_code=404, detail="Вы еще не оставили комментарии")

class SubmissionNOtFound(AllExceptions):
    def __init__(self):
        super().__init__(status_code=204, detail='Данные не найдены')

class CategoryNotFound(AllExceptions):
    def __init__(self):
        super().__init__(status_code=404, detail='категории не найдены')
        