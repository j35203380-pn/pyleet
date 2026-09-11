from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import func,DateTime
from typing import Annotated
from datetime import datetime



pk=Annotated[int,mapped_column(primary_key=True)]



class User(Base):
    __tablename__ = 'users'

    id : Mapped[pk]
    name : Mapped[str]
    nik_name : Mapped[str] = mapped_column(unique=True)
    
    email : Mapped[str] = mapped_column(unique=True)
    password : Mapped[str] 

    create_date : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    server_default=func.now()) 
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    server_default=func.now(),
                                    onupdate=func.now())
    
    submissions : Mapped[list['Submission']] = relationship(back_populates='user')
    comments : Mapped[list['Comments']] = relationship(back_populates='users')


