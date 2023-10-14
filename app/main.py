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
from app.domains.core.controller.user import user_router
from app.logs.CloudWatchLogHandler import setup_cloudwatch_logging
import logging


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
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup_event():
    logger.info("Execute Migrations")

    alembic_ini_path = settings.root_dir / 'app' / 'db' / 'migrations'

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', str(alembic_ini_path))
    alembic_cfg.set_main_option('prepend_sys_path', '.')
    alembic_cfg.set_main_option('version_path_separator', 'os')

    upgrade(alembic_cfg, "head")

    if settings.env == Environments.LOCAL.value:
        db_session = Session()
        ensure_default_user(db_session)
