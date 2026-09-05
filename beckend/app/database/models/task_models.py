from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,column_property
from sqlalchemy import ForeignKey,func,Text,Enum
from typing import Annotated
from sqlalchemy.dialects.postgresql import JSONB,UUID
from datetime import datetime
from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,Enum,func,DateTime
from typing import Annotated,Any
from datetime import datetime
from sqlalchemy import JSON,select,Integer
from config import SubmissionStatus,DifficultyLevel
from uuid import uuid4

json_type = JSON().with_variant(JSONB, "postgresql")
pk=Annotated[int,mapped_column(primary_key=True)]



class Task(Base):
    __tablename__ = 'tasks'

    id : Mapped[pk]
    title : Mapped[str]
    description : Mapped[str] = mapped_column(Text)
    difficulty : Mapped[DifficultyLevel] = mapped_column(Enum(DifficultyLevel))
    solution : Mapped[Any | None] = mapped_column(json_type)
    starter_code: Mapped[str] = mapped_column(Text)     
    method_name: Mapped[str]                            
    test_cases: Mapped[Any] = mapped_column(json_type)

    create_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())
    update_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 onupdate=func.now())

    
    submissions : Mapped[list['Submission']] = relationship(back_populates='task')
    comments : Mapped[list['Comments']] = relationship(back_populates='task')
    categories : Mapped[list['Category']] =  relationship(secondary='type_tasks',
                                                          back_populates='tasks')


    def __repr__(self):
        return self.title

 

class Comments(Base):
    __tablename__ = 'comments'

    id : Mapped[pk]
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id',ondelete='CASCADE'), index=True)
    task_id : Mapped[int] = mapped_column(ForeignKey('tasks.id',ondelete='CASCADE'), index=True)
    comment : Mapped[str] = mapped_column(Text)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  server_default=func.now())
    update_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 onupdate=func.now())
                                                 
    users : Mapped['User'] = relationship(back_populates='comments')
    task : Mapped['Task'] = relationship(back_populates='comments')
    


class Submission(Base):
    __tablename__ = 'submissions'

    id : Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
    task_id : Mapped[int] = mapped_column(ForeignKey('tasks.id',ondelete='CASCADE'),index=True)
    code : Mapped[str] = mapped_column(Text)
    status : Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus) 
                                                      ,default=SubmissionStatus.PENDING)
    exit_code : Mapped[int | None]
    output : Mapped[str | None] = mapped_column(Text)
    time_ms : Mapped[float | None]

    creadet_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  server_default=func.now())

    user : Mapped['User'] = relationship(back_populates='submissions')
    task : Mapped['Task'] = relationship(back_populates='submissions')


class TypeTask(Base):
    __tablename__ = 'type_tasks'


    categories_id : Mapped[int] = mapped_column(
                                    ForeignKey('categories.id',
                                                ondelete='CASCADE')
                                                ,primary_key=True)
    task_id : Mapped[int] = mapped_column(
                                    ForeignKey('tasks.id',
                                                ondelete='CASCADE'),
                                                primary_key=True)


class Category(Base):
    __tablename__ = 'categories'

    id : Mapped[pk]

    name: Mapped[str] = mapped_column(unique=True)

    tasks: Mapped[list['Task']]= relationship(secondary='type_tasks',
                                              back_populates='categories')

    def __rerp__(self):
        return self.name



class OutboxSub(Base):
    __tablename__ = 'outboxsub'
    
    id : Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True)
    submission_id : Mapped[UUID] = mapped_column(UUID(as_uuid=True)) 
    message : Mapped[dict]=mapped_column(json_type)
    count : Mapped[int]=mapped_column(Integer,default=0,nullable=False)
    failed_at : Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True ,default=None)
    last_error : Mapped[str|None] = mapped_column(Text,nullable=True, default=None)
    created_at : Mapped[datetime]= mapped_column(DateTime(timezone=True),server_default=func.now())
    processed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=True,default=None)



class InboxSub(Base):
    __tablename__= 'inboxsub'

    submission_id : Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True)
    payload : Mapped[dict] = mapped_column(json_type,nullable=True)
    processed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),)



Task.comments_count=column_property(
    select(func.count(Comments.id))
    .where(Comments.task_id==Task.id)
    .correlate_except(Comments)
    .scalar_subquery())
