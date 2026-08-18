from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,Enum,func,Text,JSON
from typing import Annotated,Any
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

json_type = JSON().with_variant(JSONB, "postgresql")




pk=Annotated[int,mapped_column(primary_key=True)]


class Seller(Base):
    __tablename__ = 'sellers'

    id : Mapped[pk]
    inn : Mapped[int]
    user_id : Mapped[int]=mapped_column(ForeignKey('users.id'))
    create_date : Mapped[datetime] = mapped_column(
                                    server_default=func.now()) 
    updated_at : Mapped[datetime] = mapped_column(
                                    server_default=func.now(),
                                    onupdate=func.now())
    user : Mapped['User_auth'] = relationship(back_populates='sellers')
    tasks : Mapped[list['Task']] = relationship(back_populates='seller')




class Buyer(Base):
    __tablename__ = 'buyers'

    id : Mapped[pk]
    user_id : Mapped[int]=mapped_column(ForeignKey("users.id"))
    
    user : Mapped['User_auth'] = relationship(back_populates='buyers')

    solutions : Mapped[list['TaskSolution']] = relationship(back_populates='buyer',cascade='all, delete-orphan')
    

class TaskSolution(Base):
    __tablename__ = 'task_solution'

    id : Mapped[pk]
    buyer_id : Mapped[int] = mapped_column(ForeignKey('buyers.id',ondelete='CASCADE'))
    task_id : Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    content : Mapped[Any] = mapped_column(json_type, nullable=False)
    creadet_at : Mapped[datetime] = mapped_column(server_default=func.now())

    buyer : Mapped['Buyer'] = relationship(back_populates='solutions')
    task : Mapped['Task'] = relationship(back_populates='solutions')


    
