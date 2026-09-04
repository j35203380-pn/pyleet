from httpx import AsyncClient
import pytest



@pytest.mark.asyncio(loop_scope='function')
async def test_solution_task(client: AsyncClient):
    responce=await client.get('/problems/solution/1')
    
    assert responce.status_code==200


@pytest.mark.asyncio(loop_scope='function')
async def test_task_level(client: AsyncClient):
    responce=await client.get('/problems/task/MEDIUM')

    assert responce.status_code==200


