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
    id: Optional[str]
    name: Optional[str]
    email: Optional[str]  = None
    emailVerified: Optional[datetime]  = None
    image: Optional[str]  = None
    walletPublicKey: Optional[str]  = None
    username: Optional[str]  = None
    bio: Optional[str]  = None
    role: Optional[str]  = None
    registeredAt: datetime
    jwt: Optional[str] = None
    iat: Optional[int] = None
    exp: Optional[int] = None
    jti: Optional[str] = None