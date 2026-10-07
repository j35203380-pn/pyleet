from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import joinedload,selectinload
from app.exceptions import CategoryNotFound                  
from app.database.models import Task,Category
import asyncio



_semaphore=asyncio.Semaphore(20)



class CategoryRepositories(BaseRepository):

    async def CategoriesGet(self,cat_id: int):
        async with _semaphore:
            
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
        async with _semaphore:
            c=await self._db.execute(
                select(Category)
            )
            cat=c.scalars().all()
            if not cat:
                raise CategoryNotFound()
            return cat