from typing import TYPE_CHECKING, List
import uuid
from fastapi import Depends
from sqlalchemy import Boolean, Column, DateTime, String, Uuid, func, JSON
from sqlalchemy.orm import Mapped, Relationship
from app.db.base import Base


if TYPE_CHECKING:
    from app.domains.train_job.models.train_job import TrainJob

class User(Base):
    __tablename__ = 'user'
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_id = Column(String, index=True, nullable=False)
    pubkey = Column(String, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    bio = Column(String, index=True, nullable=True)
    image_url = Column(String, index=True, nullable=True)
    status = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    player_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now())
    
    train_jobs_created: Mapped[List['TrainJob']] = Relationship(
        foreign_keys="TrainJob.created_by_id", back_populates="created_by"
    )

    #player_data: Mapped['PlayerData'] = Relationship(
    #    foreign_keys="PlayerData.created_by_id", back_populates="created_by"
    #)
