from httpx import AsyncClient
import time
from pytest import MonkeyPatch



async def test_auth_(client: AsyncClient):

    responce=await client.post('/auth/regist',
                               json={'name':'Test','nik_name':'tesname',
                                     'email': 'test@gmail.ry','password': '123123123'
                                     ,'password_confim': '123123123'})

    
    assert responce.status_code==200
    



async def test_refresh(auth_client: AsyncClient,monkeypatch: MonkeyPatch):
    real=time.time
    monkeypatch.setattr(time,'time',lambda: real()+31)
    response=await auth_client.post('/auth/refresh')
    print(response.json())
    assert response.status_code==200
    return response



