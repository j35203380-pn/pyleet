from httpx import AsyncClient
import pytest




@pytest.mark.asyncio(loop_scope='function')
async def test_add_comment(auth_client: AsyncClient):

    responce=await auth_client.post('/coments/task/1',
                                    json={'comment': 'тест коммент'})

    assert responce.status_code==201




@pytest.mark.asyncio(loop_scope='function')
async def test_get_comment(auth_client: AsyncClient):

    responce=await auth_client.get('/coments/1')

    assert responce.status_code==200



@pytest.mark.asyncio(loop_scope='function')
async def test_all_comment(auth_client: AsyncClient):

    responce=await auth_client.get('/coments/user/all')

    assert responce.status_code==200




@pytest.mark.asyncio(loop_scope='function')
async def test_all_comment_task(auth_client: AsyncClient):

    responce=await auth_client.get('/coments/task/1')

    assert responce.status_code==200



@pytest.mark.asyncio(loop_scope='function')
async def test_put_comment(auth_client: AsyncClient):

    responce=await auth_client.put('/coments/task/1',
                                    params={'comment_id':1},
                                    json={ 'comment': 'тест коммент обновлен'})

    assert responce.status_code==200


@pytest.mark.asyncio(loop_scope='function')
async def test_delete_comment(auth_client: AsyncClient):

    responce=await auth_client.delete('/coments/task/1',
                                    params={'comment_id':1})

    assert responce.status_code==200