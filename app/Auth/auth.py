

import base64
import json
import logging
from typing import Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.connection import Session, get_db_session


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


secret="f3W7NSfJpj+VpzEjgNshDRJhOGZHafFTqd7aswiOjuyOy2qm"
token="eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..2DVSzAAKewITDBwS.TbK3Qbeq-t9Nza7WamJ0mf-SpOgsrkdYE7zgq-vypqRqFGH0TxQgcLevPShcq6e3PCaZuiotZLiDW0iONZ6IN9Jv85x2v-yojT60kKpW6RK7L4HCJpoHfywoWVDUjbBkNgYr6UylpI8Uv9vOy8k18DADriW0ia21b3WLpqfbTaTrn5tkJKau8B105XH6Wr8WLsWIPFx_NwlEDOciyWoAalA-vAxz5htiqDs00kgWLknVZyWPKP34GsHR7GcbSELpUOFUarDOZ5W-9FOQLJak7OVj3HqZb_ecfgoiBbpQGlfz657yWi-jorFGdqiEJXP_ckRGvzQg23BvXSU3H3qg3SCzosU5XftX9Si346K5qjKm3JEm--zZxV4WgoiksKtlYBdCPywyJEG34_k5j056q5VM2wbEbEOmbysZQfGtbF_0LrBMbzuH0Czj_OTR4-8zeeORmhpyBJQIQhPn0dEAWWoiMimc2mTL_PwnrF51uFiQUqltwwPGyvC4mitB_mp2IkQM0DEekqRFdovpaDc55zXRNA0qT6CvMgxSoJ7bpwEb-fJgslNUrc_7FYK5N4vdH8Ea2sE8VkodLPJrM0UdESmnXMjdLVyYnXLk439SEDlgvapc4TtFBNLQF4KlBIqoIng4NS7hWphPYWkzAngY4iD-Vra6JjEJdLPYPNKmEO1Z5wllLbdw_bgC5XhOBSX3JZRa5S6BzsYTkv2XvY9B8X2P8YviVBEacjkEKCML0RuWUKBE56A-IbG-OXesyGq4alJ1XGPtMu4ROCe518Nh2ZwKrghyUIs3_xiJ_61R2pwMPhAadwF68GOWhyw0Xt24U_8D_8JBUY9gBiXgXnX1Ki5FRmQnRwqxdAARAkLam832Mb8WBhUFOpHKtIrNa0vYxhLSkecAYHFTaP3xzAjeuBfJRna4CtgbrXZrMdyJEsGD31CNHvWRd4VtARQCGCXS32Px6-OOy4eEgGTVKWp3b0s9Oj2s16m0MZlFcKKLKrWktztvlqMAD8Vq-dMh_L0y8Oa9X1mCQ8KbOTYPHfqYCZtTM6SGh7nvjUlc_EH8jLCueGsykJYpcNIUi1Yfh9Ah2H0_Qm7pdOR6UiM5Nj0YhZhSTR5t6BhYSyRYujy_1-1moTqxjl9MmksQTiQFkcS7EhdAxW9cMdN0kTKfMkcI4aDcYorJJwv4G2RDNZd86Zmex_-_dzAlpNiNWMcRJjJZArnjEOM8lIHnVuVM9kxvjz0TzI4sLBtJ3Wq9UbWplN5Sdp-7LjOnSMUlw2iEhvC3p37k.ZRZOPAWeqU_mi9zO5TrcHw"


def auth(
    db_session: Session = Depends(get_db_session),
    token = Depends(oauth_schema)
) -> UserJwtData:
    logger.info("************AUTH****************")
    user_repository = UserRepository(db_session) 
    if settings.env != Environments.LOCAL.value:
        return
    
    try:
        jwt_decoded = decrypt_jwe(token, secret)

        jwt_dict = json.loads(jwt_decoded.decode('utf-8'))
        user_jwt_data = UserJwtData(**jwt_dict)
        #logger.info(user_jwt_data)

        existing_user = user_repository.get_by_user_id(user_jwt_data.id)

        if existing_user:
            return existing_user

        user_data = map_user_data_from_jwt(user_jwt_data)

        logger.info(f"************AUTH**************** {user_data}")

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
        user_id=jwt_data.id,  
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