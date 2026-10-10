from sqlalchemy.ext.asyncio import AsyncSession



class BaseRepositories:

    def __init__(self,db: AsyncSession):

        self._db=db

