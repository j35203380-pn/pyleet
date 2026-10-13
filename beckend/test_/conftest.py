from httpx import AsyncClient,ASGITransport
from app.main import app
from test_.db import init_test_base,drop_test_base,test_aiomaker
import pytest_asyncio
from asgi_lifespan import LifespanManager
from app.database.db import get_db
from app.database.models import UserTOTP
from script_tatsk_add import add_task_script,task
from sqlalchemy import delete


async def depend_get_db():
    async with test_aiomaker() as session:
        yield session

async def main_script():
    await add_task_script(task=task,ses=test_aiomaker)


@pytest_asyncio.fixture(scope='function',loop_scope='function')
async def client():
    await init_test_base()
    await main_script()
    app.dependency_overrides[get_db]= depend_get_db
    
        
    async with LifespanManager(app) as manager:
        transport=ASGITransport(app=app)
        async with AsyncClient(transport=transport,base_url='http://test') as cl:
            yield cl

    app.dependency_overrides.clear()
    await drop_test_base()
    

@pytest_asyncio.fixture(scope="function", loop_scope='function')
async def auth_client(client: AsyncClient):

    responce=await client.post('/auth/regist',
                               json={'name':'Test','nik_name':'tesname',
                                     'email': 'test@gmail.ry','password': '123123123'
                                     ,'password_confim': '123123123'})

    
    assert responce.status_code==200

    responce= await client.post('/auth/login',
                               data={'username': 'tesname','password':"123123123"})

    assert responce.status_code==200
    refresh=responce.cookies.get('refresh_token')
    client.cookies.set('refresh_token',refresh)
    token=responce.json()['access_token']
    client.headers['Authorization']= f"Bearer {token}"

    return client

