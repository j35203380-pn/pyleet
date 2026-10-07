from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import func,DateTime,UUID,Boolean,ForeignKey,String,Text
from typing import Annotated
from datetime import datetime
import uuid


pk=Annotated[uuid.UUID,mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)]



class User(Base):
    __tablename__ = 'users'

    id: Mapped[pk]
    name: Mapped[str]
    nik_name: Mapped[str] = mapped_column(unique=True)
    
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] 
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False,nullable=True)
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    server_default=func.now()) 
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                    server_default=func.now(),
                                    onupdate=func.now())
    
    submissions: Mapped[list['Submission']] = relationship(back_populates='user')
    comments: Mapped[list['Comments']] = relationship(back_populates='users')
    sessions: Mapped[list['Session']] = relationship(back_populates='user')



class Session(Base):
    __tablename__ = 'session'

    id: Mapped[pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    abs_expire: Mapped[int] = mapped_column(nullable=False)
    user_agent: Mapped[str] = mapped_column(String,nullable=True)
    ip: Mapped[str] = mapped_column(String,nullable=True)
    
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                   server_default=func.now(),
                                                   server_onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    user: Mapped['User']= relationship(back_populates='sessions')





class TRefresh(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[pk]
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('session.id', ondelete='CASCADE'),index=True)
    token_hash: Mapped[str] = mapped_column(Text, unique=True,nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean,default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)
