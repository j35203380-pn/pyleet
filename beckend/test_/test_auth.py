from httpx import AsyncClient
import pytest



@pytest.mark.asyncio(loop_scope='function')
async def test_auth_(client: AsyncClient):

    responce=await client.post('/auth/',
                               json={'name':'Test','nik_name':'tesname',
                                     'email': 'test@gmail.ry','password': '123123123'
                                     ,'password_confim': '123123123'})

    
    assert responce.status_code==200
    return responce


