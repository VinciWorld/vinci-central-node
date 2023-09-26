from datetime import datetime
import uuid
from pydantic import BaseModel


class UserSchema(BaseModel):
    id: uuid.UUID
    user_id: str
    status: bool
    created_at: datetime
    updated_at: datetime | None