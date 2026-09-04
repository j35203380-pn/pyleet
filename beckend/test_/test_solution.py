from httpx import AsyncClient
import pytest
import logging

sol=f"""
class Solution:
    def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
        left = 0
        right = len(numbers) - 1
        while left < right:
            current_sum = numbers[left] + numbers[right]
            if current_sum == target:
                return [left, right]
            elif current_sum < target:
                left += 1
            else:
                right -= 1
        return []"""


@pytest.mark.asyncio(loop_scope='function')
async def test_run_task(auth_client: AsyncClient):
    responce=await auth_client.post('/solution/run/1',
                               json={'code':sol})

    print(responce.json())
    
    assert responce.status_code==200
    submission_id=responce.json()
    logging.info('решение отпарвлено')
    logging.info('ждем ответа... ')
    
    get_responce=await auth_client.get(f'solution/run/result/{submission_id}')

    assert get_responce.status_code==200



@pytest.mark.asyncio(loop_scope='function')
async def test_submit_task(auth_client: AsyncClient):
    responce=await auth_client.post('/solution/submit/1',
                               json={'code':sol})

    print(responce.json())
    
    assert responce.status_code==200
    submission_id=responce.json()
    logging.info('решение отпарвлено')
    logging.info('ждем ответа... ')
    
    get_responce=await auth_client.get(f'solution/submit/result/{submission_id}')

    assert get_responce.status_code==200
