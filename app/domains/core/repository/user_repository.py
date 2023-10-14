import logging
import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db_session
from app.domains.core.models.user import User

from app.domains.core.schemas.user import UserCreate, UserSchema, UserUpdate

logger = logging.getLogger(__name__) 

class UserRepository():
    def __init__(self, db:Session):
        self.db = db


    def get_by_pubKey(self, pubkey) -> UserSchema:
        model = self.db.query(User).filter_by(pubkey=pubkey).first()

        if not model:
            return None

        return UserSchema.model_validate(model)
    

    def get_by_user_id(self, user_id_dapp: str) -> UserSchema:
        model = self.db.query(User).filter_by(user_id=user_id_dapp).first()

        if not model:
            return None

        return UserSchema.model_validate(model)
        
    def set_user_active(self, user_id_dapp: str) -> UserSchema:
        model = self.db.query(User).filter_by(user_id=user_id_dapp).first()

        if not model:
            return None
        
        model.status = True
        self.db.commit()
        self.db.refresh(model)

        return UserSchema.model_validate(model)


    def register_user(self, user: UserCreate) -> UserSchema:
        user_db = User(**user.__dict__)

        self.db.add(user_db)
        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema.model_validate(user_db)
    
    def create_user(self, user: UserCreate) -> UserSchema:
        user_db = User(**user.__dict__)

        self.db.add(user_db)
        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema.model_validate(user_db)
    

    def update_user(self, user_id: str, user_update: UserUpdate) -> UserSchema:

        user_db = self.db.query(User).filter(User.user_id == user_id).first()
        logger.info(user_db)
        if not user_db:
            return None

        for key, value in user_update.dict().items():
            if value is not None: 
                setattr(user_db, key, value)

        self.db.commit()
        self.db.refresh(user_db)

        return UserSchema.model_validate(user_db)


    def update_player_data(self, user_id: str, player_data: str) -> UserSchema:
        user_db = self.db.query(User).filter(User.user_id == user_id).first()

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
    
    return UserSchema.model_validate(user)