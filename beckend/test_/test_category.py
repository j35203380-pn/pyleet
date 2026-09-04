from httpx import AsyncClient
import pytest



@pytest.mark.asyncio(loop_scope='function')
async def test_category_get(client: AsyncClient):
    responce=await client.get('/category/all')

    assert responce.status_code==200



@pytest.mark.asyncio(loop_scope='function')
async def test_get_task(client: AsyncClient):
    responce=await client.get('/category/task/1')

    assert responce.status_code==200