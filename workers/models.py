from db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,func,Text,Enum,JSON,Integer,DateTime
from typing import Annotated
from sqlalchemy.dialects.postgresql import JSONB,UUID
from datetime import datetime
from shemas import SubmissionStatus
from uuid import uuid4

json_type = JSON().with_variant(JSONB, "postgresql")
pk=Annotated[int,mapped_column(primary_key=True)]





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





class OutboxSub(Base):
    __tablename__ = 'outboxsub'
    
    submission_id : Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True) 
    message : Mapped[dict]=mapped_column(json_type)
    count : Mapped[int]=mapped_column(Integer,default=0,nullable=False)
    failed_at : Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True ,default=None,index=True)
    last_error : Mapped[str|None] = mapped_column(Text,nullable=True, default=None)
    last_attempt_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=True,default=None)
    created_at : Mapped[datetime]= mapped_column(DateTime(timezone=True),server_default=func.now())
    processed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=True,default=None,index=True)



class InboxSub(Base):
    __tablename__= 'inboxsub'

    submission_id : Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True)
    payload : Mapped[dict] = mapped_column(json_type,nullable=True)
    processed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),)


