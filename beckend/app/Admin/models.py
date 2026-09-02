from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from app.database.models import Task,Category
import logging

class AdminAuth(AuthenticationBackend):

    async def login(self,request: Request):
        form=await request.form()
        username,password=form['username'],form['password']
        logging.info("напсиал паролб")
        if username=='admin_' and password=='admin__':
            logging.info('вход успешно выполнен')
            request.session.update({'token': username})
            return True
        logging.error('не правильно ведены данные')
        return False

    async def logout(self, request:Request):
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token=request.session.get('token')
        if not token:
            return False
        return True

authenfication_backend=AdminAuth(secret_key='sahvnpsdgvghvypguierhntv5807ytn34v57235638593487v3073v25329406vn34789v234086v4vunmtuve[0tvuerwiove')


class UserAdminTask(ModelView,model=Task):
    column_list=[Task.id,Task.title,Task.description,
                 Task.difficulty,Task.solution,
                 Task.starter_code,Task.method_name,
                 Task.test_cases,Task.categories]
    
    form_columns=[Task.id,Task.title,Task.description,
                 Task.difficulty,Task.solution,
                 Task.starter_code,Task.method_name,
                 Task.test_cases,Task.categories]

class UserAdminCategory(ModelView,model=Category):
    column_list=[Category.id,Category.name,Category.tasks]

    form_columns=[Category.id,Category.name,Category.tasks]