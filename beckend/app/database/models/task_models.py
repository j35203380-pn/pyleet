from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import ForeignKey,Enum,func,Text
from typing import Annotated
from sqlalchemy.dialects.postgresql import JSONB 
from datetime import datetime
from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,Enum,func,DateTime
from typing import Annotated,Any
from datetime import datetime
from sqlalchemy import JSON

json_type = JSON().with_variant(JSONB, "postgresql")
pk=Annotated[int,mapped_column(primary_key=True)]



class Task(Base):
    __tablename__ = 'tasks'

    id : Mapped[pk]
    name : Mapped[str]
    seller_id : Mapped[int] = mapped_column(ForeignKey('sellers.id', ondelete="CASCADE"))
    
    seller : Mapped["Seller"] = relationship(back_populates='tasks')
    proviso : Mapped['Proviso'] = relationship(back_populates='task',uselist=False,cascade='save-update, merge')
    solutions : Mapped[list['TaskSolution']] = relationship(back_populates='task')
    comments : Mapped[list['Comments']] = relationship(back_populates='task')

    create_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    update_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),
                                                                         onupdate=func.now())


class Proviso(Base):
    __tablename__ = 'provision'

    id : Mapped[pk]
    task_id: Mapped[int]= mapped_column(ForeignKey('tasks.id',ondelete="CASCADE"),unique=True)
    text : Mapped[str] = mapped_column(Text)
    solution : Mapped[Any | None] = mapped_column(json_type, nullable=True)

    task : Mapped['Task'] = relationship(back_populates='proviso',
                                         uselist=False)



class Comments(Base):
    __tablename__ = 'comments'

    id : Mapped[pk]
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id',ondelete='CASACDE'), index=True)
    task_id : Mapped[int] = mapped_column(ForeignKey('tasks.id',ondelete='CASCADE'), index=True)
    comment : Mapped[str] = mapped_column(Text)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  server_default=func.now())

    users : Mapped['User_auth'] = relationship(back_populates='comments')
    task : Mapped['Task'] = relationship(back_populates='comments')
