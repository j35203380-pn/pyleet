from app.database.db import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload,selectinload
from app.exceptions import CategoryNotFound                  
from app.database.models import Task,Category
import asyncio


LimitDB=asyncio.Semaphore(20)



class CategoryRepositories:

    def __init__(self, db: AsyncSession):
        self._db=db



    async def CategoriesGet(self,cat_id: int):
        async with LimitDB:
            
            cat=await self._db.execute(
                select(Category)
                .options(selectinload(Category.tasks)
                         .load_only(Task.id,Task.title,Task.difficulty))
                .where(Category.id==cat_id)
            )

            t=cat.scalar_one_or_none()
            if not t:
                raise CategoryNotFound()
            return t



    async def CategoriesAll(self):
        async with LimitDB:
            c=await self._db.execute(
                select(Category)
            )
            cat=c.scalars().all()
            if not cat:
                raise CategoryNotFound()
            return cat