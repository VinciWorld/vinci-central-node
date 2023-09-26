from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel
from app.domains.core.schemas.user import UserSchema

from app.domains.train_job.schemas.train_job_constants import TrainJobStatus, TrainJobType


class TrainJobQueue(BaseModel):
    centra_node_id: uuid.UUID
    central_node_url: str
    run_id: uuid.UUID
    job_type: TrainJobType
    nn_model_config: str
    agent_config: str
    env_config: str


class TrainJobsBase(BaseModel):
    run_id: uuid.UUID
    job_status: TrainJobStatus
    job_type: TrainJobType
    nn_model_config: str
    agent_config: str
    env_config: str


class TrainJobCreate(TrainJobsBase):
    pass


class TrainJobSchema(TrainJobsBase):
    id: uuid.UUID
    created_at: datetime
    created_by: UserSchema

    class Config:
        from_attributes=True


class TrainJobResponseSchema(TrainJobSchema):
    pass


class TrainJobBody(BaseModel):
    run_id: Optional[uuid.UUID] | None = None
    agent_config: str
    env_config: str
    nn_model_config: str