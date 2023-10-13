from typing import TYPE_CHECKING
import uuid
from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, Uuid, func
from sqlalchemy.orm import Mapped, Relationship
from app.db.base import Base
from app.domains.train_job.schemas.train_job_constants import TrainJobStatus, TrainJobType

if TYPE_CHECKING:
    from app.domains.core.models.user import User

class PlayerData():
    __tablename__ = "player_data"
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    created_by_id: Mapped[Uuid] = Column(ForeignKey("user.id"))
    created_by: Mapped['User'] = Relationship(
        foreign_keys=[created_by_id], back_populates="player_data"
    )
