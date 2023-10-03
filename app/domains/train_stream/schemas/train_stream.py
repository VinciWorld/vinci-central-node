import uuid
from pydantic import BaseModel

from app.domains.train_stream.schemas.constants import TrainNodeStateEnum


class StreamMessage(BaseModel):
    msg_id: str

class TrainRunId(StreamMessage):
    run_id: uuid.UUID

class TrainNodeStateStream(StreamMessage):
    state: TrainNodeStateEnum

class TrainNodeDataStream(StreamMessage):
    data: str