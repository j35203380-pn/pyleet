from httpx import AsyncClient
import pytest_asyncio, time
from pytest import MonkeyPatch



basa='/2fa'

nik_name='tesname'
email='test@gmail.ry'
password= '123123123'







@pytest_asyncio.fixture
async def f2a_code(auth_client: AsyncClient):
    response=await auth_client.post(f'{basa}/setup/code')

    assert response.status_code==200
    code=response.json()
    auth_client.headers['code']=code
    return auth_client


async def test_add_code_2fa(f2a_code: AsyncClient):
    code=f2a_code.headers['code']

    response=await f2a_code.post(f'{basa}/setup/verify',
                                       params={'code': code})

    print(response.json())
    assert response.status_code==200



async def test_login_2fa(auth_client: AsyncClient,monkeypatch: MonkeyPatch):
    r=await auth_client.post(f'{basa}/setup/code')
    assert r.status_code==200
    code=r.json()

    r=await auth_client.post(f'{basa}/setup/verify',params={'code': code})
    assert r.status_code==200

    auth_client.headers.pop('Authorization', None)    
    real=time.time
    monkeypatch.setattr(time,'time',lambda: real()+31)
    response=await auth_client.post(f'{basa}/login/code',
                           data={'username': nik_name,
                                 'password': password})
    print(r.status_code, r.json())
    assert response.status_code==200
    
    
    code=response.json()['code']
    token=response.json()['access']
    auth_client.headers['Authorization']=f'bearer {token}'
    auth_client.headers['code']=code



    response=await auth_client.post(f'{basa}/code',
                                       params={'code': code})

    assert response.status_code==200