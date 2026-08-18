from fastapi import HTTPException,Depends
from app.auth.auth import current_token
from typing import Annotated

CurUs=Annotated[dict,Depends(current_token)]



class  ReschePoints:

    def __init__(self,*role: str):

        if not role:
            raise ValueError("Необходимо указать хотя бы одну роль для проверки!")

        self._role=role

    async def __call__(self, user: CurUs):

        if user['role'] not in self._role:
            raise HTTPException(status_code=404 ,detail='Нет доступа')

        
        return user