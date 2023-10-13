import string
import uuid
from fastapi import APIRouter, Depends
from pytest import Session
from app.db.connection import get_db_session
from app.domains.core.repository.user_repository import UserRepository

from app.domains.core.schemas.user import UserCreate, UserSchema


train_job_router = APIRouter(
    prefix='/api/v1',
    tags=["User"]
)


@train_job_router.get("/user", response_model=UserSchema)
async def get_user(
    pubkey: str,
    db_session: Session = Depends(get_db_session)
):
    
    repository = UserRepository(db_session)

    user = repository.get_by_pubKey(pubkey)

    return user


@train_job_router.patch("/user/{pubkey}/player-data", response_model=UserSchema)
async def save_user_player_data(
    pubkey:str,
    player_data: str,
    db_session: Session = Depends(get_db_session)
):
    
    repository = UserRepository(db_session)

    user = repository.update_player_data(pubkey, player_data)

    return user