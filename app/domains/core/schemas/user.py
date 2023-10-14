from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel


class UserBase(BaseModel):
   
    pubkey: str
    username: str 
    bio: Optional[str] = None
    image_url: Optional[str] = None
    player_data: Optional[str] = None

class UserCreate(UserBase):
    user_id: str
    is_admin: bool = False
    status: bool = True
    pass

class UserUpdate(UserBase):
    pubkey: Optional[str] = None
    username:  Optional[str] = None 
    pass

class UserSchema(UserBase):
    id: uuid.UUID
    user_id: str
    is_admin: bool = False
    status: bool = True
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes=True


class UserJwtData(BaseModel):
    id: str
    name: str
    email: str
    emailVerified: Optional[datetime]
    image: str
    walletPublicKey: Optional[str]
    username: Optional[str]
    bio: Optional[str]
    role: str
    registeredAt: datetime
    jwt: str
    iat: int
    exp: int
    jti: str