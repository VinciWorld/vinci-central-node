import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db_session
from app.domains.core.models.user import User

from app.domains.core.schemas.user import UserCreate, UserSchema, UserUpdate


class UserRepository():
    def __init__(self, db:Session):
        self.db = db


    def get_by_pubKey(self, pubkey):
        model = self.db.query(User).filter_by(pubkey=pubkey).first()

        if not model:
            return None

        return UserSchema.model_validate(model)

    def register_user(self, user: UserCreate):
        user_db = User(**user.__dict__)

        self.db.add(user_db)
        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema(
            id=user_db.id,
            username=user_db.username,
            bio=user_db.bio,
            image_url=user_db.image_url,
            user_id=user_db.user_id,
            status=user_db.status,
            playerData=user_db.player_data,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at
        )
    
    def create_user(self, user: UserCreate):
        user_db = User(**user.__dict__)

        self.db.add(user_db)
        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema.model_validate(user_db)
    

    def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> UserSchema:

        user_db = self.db.query(User).filter(User.id == user_id).first()

        if not user_db:
            return None

        for key, value in user_update.dict().items():
            if value is not None: 
                setattr(user_db, key, value)

        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema.model_validate(user_db)


    def update_player_data(self, pub_key: str, player_data: str) -> UserSchema:
        user_db = self.db.query(User).filter(User.pubkey == pub_key).first()

        if not user_db:
            return None

        user_db.player_data = player_data

        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema.model_validate(user_db)




def ensure_default_user(db: Session):
    default_user = db.query(User).filter_by(user_id="f76b7d2c-8643-4633-afe5-184430818ccf").first()
    if not default_user:
        default_user = User(
            user_id="f76b7d2c-8643-4633-afe5-184430818ccf",
            pubkey="32423",
            username="costasdasd",
            status=True,
            is_admin=True
            )
        db.add(default_user)
        db.commit()

def get_default_user(db: Session = Depends(get_db_session)) -> UserSchema:
    user = db.query(User).filter_by(user_id="f76b7d2c-8643-4633-afe5-184430818ccf").first()

    return UserSchema(
        id=user.id,
        user_id=user.user_id,
        pubkey="32423",
        username="costasdasd",
        status=user.status,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )