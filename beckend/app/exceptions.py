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


class UserTokenError(AllExceptions):
    def __init__(self):
        super().__init__(status_code=400,detail='зайдите снова')


class TotpNotFound(AllExceptions):
    def __init__(self):
        super().__init__(status_code=404, detail='Ошибка,пройдите верификацию заного!')

class TotpLockedUntil(AllExceptions):
    def __init__(self):
        super().__init__(status_code = 404, detail='Слишком много попыток!')


class TotpErrorUsedTime(AllExceptions):
    def __init__(self):
        super().__init__(status_code = 404, detail='Слишком много попыток!')


class TotpConflictUser(AllExceptions):
    def __init__(self):
        super().__init__(status_code=409, detail='двузфакторная авторизация уже включена')

class TotpErrorCode(AllExceptions):
    def __init__(self):
        super().__init__(status_code=404, detail='неправильный код')


class UserIsBlocked(AllExceptions):
    def __init__(self):
        super().__init__(status_code=429, detail='мы ограничили доступ к вашему аккаунту')