from httpx import AsyncClient,ASGITransport
from app.main import app
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from app.database.db import test_base

@pytest_asyncio.fixture(scope='function',loop_scope='function')
async def client():
    await test_base()
    async with LifespanManager(app) as manager:
        transport=ASGITransport(app=app)
        async with AsyncClient(transport=transport,base_url='http://test') as cl:
            yield cl


@pytest_asyncio.fixture(scope="function", loop_scope='function')
async def auth_client(client: AsyncClient):

    responce= await client.post('/auth/login',
                               data={'username': 'tesname','password':"123123123"})

    assert responce.status_code==200
    token=responce.json()['access_token']
    client.headers['Authorization']= f"Bearer {token}"

    return client

