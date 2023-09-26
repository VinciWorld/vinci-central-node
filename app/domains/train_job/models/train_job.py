from typing import TYPE_CHECKING
import uuid
from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, Uuid, func
from sqlalchemy.orm import Mapped, Relationship
from app.db.base import Base
from app.domains.train_job.schemas.train_job_constants import TrainJobStatus, TrainJobType

if TYPE_CHECKING:
    from app.domains.core.models.user import User

class TrainJob(Base):
    __tablename__ = "train_job"
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    run_id = Column(Uuid, index=True, nullable=False)
    job_status = Column(Enum(TrainJobStatus), index=True, nullable=False)
    job_type = Column(Enum(TrainJobType), index=True, nullable=False)
    priority = Column(Integer, nullable=False, default=1)
    train_node_id = Column(Uuid, index=True, nullable=True)
    nn_model_config = Column(JSON, nullable=False)
    env_config = Column(JSON, nullable=False)
    agent_config = Column(JSON, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    created_by_id: Mapped[Uuid] = Column(ForeignKey("user.id"))
    created_by: Mapped["User"] = Relationship(
        foreign_keys=[created_by_id], back_populates="train_jobs_created"
    )
