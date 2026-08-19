from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import Enum,func
from typing import Annotated
import enum
from datetime import datetime





pk=Annotated[int,mapped_column(primary_key=True)]

class Rolename(str, enum.Enum):
    buyer = 'buyer'
    seller = 'seller'



class User_auth(Base):
    __tablename__ = 'users'

    id : Mapped[pk]
    name : Mapped[str]
    nik_name : Mapped[str] = mapped_column(unique=True)
    role : Mapped[str] = mapped_column(Enum(Rolename),
                                       default=Rolename.buyer)
    email : Mapped[str] = mapped_column(unique=True)
    password : Mapped[str]

    create_date : Mapped[datetime] = mapped_column(
                                    server_default=func.now()) 
    updated_at : Mapped[datetime] = mapped_column(
                                    server_default=func.now(),
                                    onupdate=func.now())
    sellers : Mapped['Seller'] = relationship(back_populates='user')
    buyers : Mapped['Buyer'] = relationship(back_populates='user')
    comments : Mapped[list['Comments']] = relationship(back_populates='users')

