from fastapi import FastAPI
from app.db.connection import Session
from app.domains.core.models.user import ensure_default_user
from alembic.config import Config
from alembic.command import upgrade
from app.settings.settings import settings
import logging



logging.config.fileConfig('logging.conf', disable_existing_loggers=False)  #type: ignore
logger = logging.getLogger(__name__) 


app = FastAPI()



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