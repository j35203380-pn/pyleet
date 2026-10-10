from app.database.db import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import func,DateTime,UUID,ForeignKey,String,LargeBinary,BOOLEAN
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
    is_active: Mapped[bool] = mapped_column(BOOLEAN,default=True,nullable=True)
    is_blocked: Mapped[bool] = mapped_column(BOOLEAN, default=False,nullable=True)
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
    token_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True,nullable=False)
    abs_expire: Mapped[int] = mapped_column(nullable=False)
    user_agent: Mapped[str] = mapped_column(String,nullable=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    ip_adress: Mapped[str] = mapped_column(String,nullable=True)
    revoked: Mapped[bool] = mapped_column(BOOLEAN,default=False)

    
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                   server_default=func.now(),
                                                   server_onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    user: Mapped['User']= relationship(back_populates='sessions')




