from fastapi import FastAPI
from app.db.connection import Session
from alembic.config import Config
from alembic.command import upgrade
from fastapi.middleware.cors import CORSMiddleware
from app.domains.core.repository.user_repository import ensure_default_user
from app.settings.settings import Environments, settings
from app.domains.train_job.controller.train_job import train_job_router
from app.domains.train_results.controllers.train_results import train_results_router
from app.domains.train_stream.controllers.train_stream import train_stream_router
from app.logs.CloudWatchLogHandler import setup_cloudwatch_logging
import logging
from decouple import config

from jose import jwt, jwk, jwe
from cryptography.hazmat.primitives import serialization
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

log_group_name = "vinci-world-cloud-dev-CentralNodeLogGroup"

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)  #type: ignore

logging.info('Setting up cloudwatch logging')
logger = logging.getLogger(__name__) 


if settings.env != Environments.LOCAL.value:
    setup_cloudwatch_logging(log_group_name)


app = FastAPI()
app.include_router(train_job_router)
app.include_router(train_stream_router)
app.include_router(train_results_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

secret="f3W7NSfJpj+VpzEjgNshDRJhOGZHafFTqd7aswiOjuyOy2qm"

secret1="f3W7NSfJpj+VpzEjgNshDRJhOGZHafFTqd7aswiOjuyOy2qm"
token="eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..2DVSzAAKewITDBwS.TbK3Qbeq-t9Nza7WamJ0mf-SpOgsrkdYE7zgq-vypqRqFGH0TxQgcLevPShcq6e3PCaZuiotZLiDW0iONZ6IN9Jv85x2v-yojT60kKpW6RK7L4HCJpoHfywoWVDUjbBkNgYr6UylpI8Uv9vOy8k18DADriW0ia21b3WLpqfbTaTrn5tkJKau8B105XH6Wr8WLsWIPFx_NwlEDOciyWoAalA-vAxz5htiqDs00kgWLknVZyWPKP34GsHR7GcbSELpUOFUarDOZ5W-9FOQLJak7OVj3HqZb_ecfgoiBbpQGlfz657yWi-jorFGdqiEJXP_ckRGvzQg23BvXSU3H3qg3SCzosU5XftX9Si346K5qjKm3JEm--zZxV4WgoiksKtlYBdCPywyJEG34_k5j056q5VM2wbEbEOmbysZQfGtbF_0LrBMbzuH0Czj_OTR4-8zeeORmhpyBJQIQhPn0dEAWWoiMimc2mTL_PwnrF51uFiQUqltwwPGyvC4mitB_mp2IkQM0DEekqRFdovpaDc55zXRNA0qT6CvMgxSoJ7bpwEb-fJgslNUrc_7FYK5N4vdH8Ea2sE8VkodLPJrM0UdESmnXMjdLVyYnXLk439SEDlgvapc4TtFBNLQF4KlBIqoIng4NS7hWphPYWkzAngY4iD-Vra6JjEJdLPYPNKmEO1Z5wllLbdw_bgC5XhOBSX3JZRa5S6BzsYTkv2XvY9B8X2P8YviVBEacjkEKCML0RuWUKBE56A-IbG-OXesyGq4alJ1XGPtMu4ROCe518Nh2ZwKrghyUIs3_xiJ_61R2pwMPhAadwF68GOWhyw0Xt24U_8D_8JBUY9gBiXgXnX1Ki5FRmQnRwqxdAARAkLam832Mb8WBhUFOpHKtIrNa0vYxhLSkecAYHFTaP3xzAjeuBfJRna4CtgbrXZrMdyJEsGD31CNHvWRd4VtARQCGCXS32Px6-OOy4eEgGTVKWp3b0s9Oj2s16m0MZlFcKKLKrWktztvlqMAD8Vq-dMh_L0y8Oa9X1mCQ8KbOTYPHfqYCZtTM6SGh7nvjUlc_EH8jLCueGsykJYpcNIUi1Yfh9Ah2H0_Qm7pdOR6UiM5Nj0YhZhSTR5t6BhYSyRYujy_1-1moTqxjl9MmksQTiQFkcS7EhdAxW9cMdN0kTKfMkcI4aDcYorJJwv4G2RDNZd86Zmex_-_dzAlpNiNWMcRJjJZArnjEOM8lIHnVuVM9kxvjz0TzI4sLBtJ3Wq9UbWplN5Sdp-7LjOnSMUlw2iEhvC3p37k.ZRZOPAWeqU_mi9zO5TrcHw"


@app.on_event("startup")
async def startup_event():
    logger.info("Execute Migrations")

    alembic_ini_path = settings.root_dir / 'app' / 'db' / 'migrations'

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', str(alembic_ini_path))
    alembic_cfg.set_main_option('prepend_sys_path', '.')
    alembic_cfg.set_main_option('version_path_separator', 'os')

    upgrade(alembic_cfg, "head")

    db_session = Session()
    ensure_default_user(db_session)

    print("tesste")
    jwt = decrypt_jwe(token, secret)
    logger.info(jwt)


def decrypt_jwe(token, secret):
    derived_encryption = get_derive_encryption_key(secret)
    
    decrypted_token = jwe.decrypt(token, derived_encryption)
    
    return decrypted_token


def get_derive_encryption_key(secret):

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


def decrypt_jwt_old(token, secret_key_derived):

    logger.info("derivaed: " + get_derive_encryption_key(secret_key_derived))   

    key = {
        "k": get_derive_encryption_key(secret_key_derived), 
        "kty": "oct",
        "alg": "dir",
        "enc": "A256GCM"
    }

    key_obj = jwk.construct(key)
    decrypted_jwt = jwe.decrypt(token, key_obj)
    
    return decrypted_jwt



