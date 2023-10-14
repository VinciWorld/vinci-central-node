import logging
import string
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from pytest import Session
from app.Auth.auth import auth, generate_token
from app.db.connection import get_db_session
from app.domains.core.repository.user_repository import UserRepository

from app.domains.core.schemas.user import UserCreate, UserSchema, UserUpdate
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__) 

user_router = APIRouter(
    prefix='/api/v1',
    tags=["User"]
)


class LoginRequest(BaseModel):
    username: str
    password: str


@user_router.post("/user/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    hardcoded_username = "costa"
    hardcoded_password = "costa"

    if data.username == hardcoded_username and data.password == hardcoded_password:
        token = generate_token(data.username, data.password)
        return {"token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")



@user_router.get("/user", response_model=UserSchema)
async def get_user(
    user: UserSchema = Depends(auth),
    db_session: Session = Depends(get_db_session)
):
    
    repository = UserRepository(db_session)

    user = repository.get_by_user_id(user.id)

    return user



@user_router.patch("/user", response_model=UserSchema)
async def save_user_player_data(
    user_update: UserUpdate,
    user: UserSchema = Depends(auth),
    db_session: Session = Depends(get_db_session)
):
    
    repository = UserRepository(db_session)

    user = repository.update_user(user.id, user_update)

    return user


@user_router.post("/user/unity-login")
def unity_login(
    user_update_body: UserUpdate,
    user: UserSchema = Depends(auth),
    db_session: Session = Depends(get_db_session)
) -> UserSchema:

    repository = UserRepository(db_session)

    logger.info(user_update_body)

    repository.update_user(user.user_id, user_update_body)
    user = repository.set_user_active(user.user_id)

    
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user
    




