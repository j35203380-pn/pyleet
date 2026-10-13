from httpx import AsyncClient
import pytest_asyncio



@pytest_asyncio.fixture
async def add_comment(auth_client: AsyncClient):

    responce=await auth_client.post('/coments/task/1',
                                    json={'comment': 'тест коммент'})

    assert responce.status_code==201
    return auth_client




async def test_get_comment(add_comment: AsyncClient):

    responce=await add_comment.get('/coments/1')

    assert responce.status_code==200



async def test_all_comment(add_comment: AsyncClient):

    responce=await add_comment.get('/coments/user/all')

    assert responce.status_code==200




async def test_all_comment_task(add_comment: AsyncClient):

    responce=await add_comment.get('/coments/task/1')

    assert responce.status_code==200



async def test_put_comment(add_comment: AsyncClient):

    responce=await add_comment.put('/coments/task/1',
                                    params={'comment_id':1},
                                    json={ 'comment': 'тест коммент обновлен'})

    assert responce.status_code==200


async def test_delete_comment(add_comment: AsyncClient):

    responce=await add_comment.delete('/coments/task/1',
                                    params={'comment_id':1})

    assert responce.status_code==200