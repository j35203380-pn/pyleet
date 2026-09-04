from app.database.models import Task,Category
from app.database.db import AsyncLocal
from sqlalchemy import select,insert
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

task ={
        "title": "Сумма двух чисел на отсортированном массиве (Two Sum II)",
        "description": (
            "Дан отсортированный по возрастанию массив целых чисел numbers и целевое число target. "
            "Найдите два числа так, чтобы их сумма составляла target.\n\n"
            "Функция должна вернуть индексы этих двух чисел (в виде списка/массива из двух элементов). "
            "Предполагается, что существует ровно одно решение, и нельзя использовать один и тот же элемент дважды.\n\n"
            "Вы должны решить эту задачу с пространственной сложностью O(1), используя метод двух указателей."
        ),
        "difficulty": "MEDIUM",  
        "starter_code": (
            "class Solution:\n"
            "   def two_sum_sorted(numbers: list[int], target: int) -> list[int]:\n"
            "        # Напишите свое решение здесь\n"
            "        pass"
        ),
        "method_name": "two_sum_sorted",
        "solution": (
            "def two_sum_sorted(numbers: list[int], target: int) -> list[int]:\n"
            "    left = 0\n"
            "    right = len(numbers) - 1\n"
            "    while left < right:\n"
            "        current_sum = numbers[left] + numbers[right]\n"
            "        if current_sum == target:\n"
            "            return [left, right]\n"
            "        elif current_sum < target:\n"
            "            left += 1\n"
            "        else:\n"
            "            right -= 1\n"
            "    return []"
        ),
        "test_cases": [
            {
                "input": {"numbers":[2,7,11,15], "target": 9},
                "expected": [0, 1]
            },
            {
                "input": {"numbers":[2,3,4], "target": 6},
                "expected": [0, 2]
            },
            {
                "input": {"numbers": [-1, 0], "target": -1},
                "expected": [0, 1]
            },
            {
                "input": {"numbers":[1,2,3,4,6,8,10], "target": 13},
                "expected": [2, 6] 
            }
        ]
    }


async def add_task_script(task: dict):
    async with AsyncLocal() as session:
        async with session.begin():
            cat_=await session.execute(
                select(Category)
                .where(Category.name=='Two Sum')
            )
            
            category_=cat_.scalar_one_or_none()
            
            if not category_:
                category_= Category(name='Two Sum')
            
            new_task=Task(**task)
            new_task.categories.append(category_)
            session.add(new_task)
            
        logging.info('задания добавлены')


async def main():

    await add_task_script(task)

asyncio.run(main())
