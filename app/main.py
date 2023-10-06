from fastapi import FastAPI
from app.db.connection import Session
from app.domains.core.models.user import ensure_default_user
from alembic.config import Config
from alembic.command import upgrade
from app.settings.settings import settings
from app.domains.train_job.controller.train_job import train_job_router
from app.domains.train_results.controllers.train_results import train_results_router
from app.domains.train_stream.controllers.train_stream import train_stream_router

import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)  #type: ignore
logger = logging.getLogger(__name__) 


app = FastAPI()
app.include_router(train_job_router)
app.include_router(train_stream_router)
app.include_router(train_results_router)



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