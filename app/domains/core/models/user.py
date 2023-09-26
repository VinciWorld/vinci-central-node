from typing import TYPE_CHECKING, List
import uuid
from fastapi import Depends
from sqlalchemy import Boolean, Column, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, Relationship
from app.db.base import Base
from sqlalchemy.orm import Session
from app.db.connection import get_db_session
from app.domains.core.schemas.user import UserSchema


if TYPE_CHECKING:
    from app.domains.train_job.models.train_job import TrainJob

class User(Base):
    __tablename__ = 'user'
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now())
    
    train_jobs_created: Mapped[List['TrainJob']] = Relationship(
        foreign_keys="TrainJob.created_by_id", back_populates="created_by"
    )


def ensure_default_user(db: Session):
    default_user = db.query(User).filter_by(user_id="f76b7d2c-8643-4633-afe5-184430818ccf").first()
    if not default_user:
        default_user = User(user_id="f76b7d2c-8643-4633-afe5-184430818ccf", status=True)
        db.add(default_user)
        db.commit()

def get_default_user(db: Session = Depends(get_db_session)) -> UserSchema:
    user = db.query(User).filter_by(user_id="f76b7d2c-8643-4633-afe5-184430818ccf").first()

    return UserSchema(
        id=user.id,
        user_id=user.user_id,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at
    )