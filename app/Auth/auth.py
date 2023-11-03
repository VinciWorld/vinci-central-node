

import base64
import json
import logging
from typing import Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.connection import Session, get_db_session

from decouple import config
from jose import jwe
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from app.domains.core.repository.user_repository import UserRepository
from app.domains.core.schemas.user import UserCreate, UserJwtData, UserSchema
from jose import jwt
from cryptography.fernet import Fernet

from app.settings.settings import Environments, settings

logger = logging.getLogger(__name__) 

oauth_schema = OAuth2PasswordBearer(tokenUrl='/api/v1/user/login')


secret=config("SECRET")


def auth(
    db_session: Session = Depends(get_db_session),
    token = Depends(oauth_schema)
) -> UserSchema:
    user_repository = UserRepository(db_session) 
    #if settings.env != Environments.LOCAL.value:
    #    return
    
    try:
        jwt_decoded = decrypt_jwe(token, secret)

        jwt_dict = json.loads(jwt_decoded.decode('utf-8'))
        user_jwt_data = UserJwtData(**jwt_dict)

        existing_user = user_repository.get_by_external_id(user_jwt_data.id)

        if existing_user:
            logger.info(f"Existing user: {existing_user}")
            return existing_user

        user_data = map_user_data_from_jwt(user_jwt_data)

        logger.info(f"Register new user {user_data}")

        return user_repository.register_user(user_data)

    except Exception as e:
        logger.error(f"Error during JWT decryption: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def decrypt_jwe(token, secret):
    derived_encryption = get_derive_encryption_key(secret)
    
    decrypted_token = jwe.decrypt(token, derived_encryption)
    
    return decrypted_token


def get_derive_encryption_key(secret: str):

    backend = default_backend()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"NextAuth.js Generated Encryption Key",
        backend=backend
    )
    
    derived_key = hkdf.derive(secret.encode('utf-8'))
    return derived_key


def map_user_data_from_jwt(jwt_data: UserJwtData) -> UserCreate:
    return UserCreate(
        external_id=jwt_data.id,  
        pubkey="",
        username=jwt_data.name,  
        image_url=jwt_data.image,
        status=False,
        is_admin=False
    )


def generate_token(username: str, password: str):

    payload = {
        "id": "some_unique_id",
        "user_id":"asasd",
        "name": username,
        "walletPublicKey": password, 
        "image": "some_image_url",
        "isAdmin": True
    }
    
    jwt_token = jwt.encode(payload, secret, algorithm='HS256')


    encrypted_token = encrypt_jwe(jwt_token, secret)

    return encrypted_token

def encrypt_jwe(token, secret):

    logger.info(get_derive_encryption_key(secret))

    fernet_key = base64.urlsafe_b64encode(get_derive_encryption_key(secret))
    derived_encryption = fernet_key
    
    cipher_suite = Fernet(derived_encryption)
    encrypted_token = cipher_suite.encrypt(token.encode())
    
    return encrypted_token