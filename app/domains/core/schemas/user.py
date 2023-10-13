from datetime import datetime
import uuid
from pydantic import BaseModel


class UserBase(BaseModel):
    id: uuid.UUID
    user_id: str
    pubkey: str
    username: str 
    bio: str | None
    image_url: str | None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserSchema(BaseModel):
    is_admin: bool
    status: bool
    created_at: datetime
    updated_at: datetime | None
    playerData: str

    class Config:
        from_attributes=True