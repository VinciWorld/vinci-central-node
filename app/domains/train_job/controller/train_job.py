import logging
import threading
import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.db.connection import get_db_session
from app.domains.core.models.user import get_default_user
from app.domains.core.schemas.user import UserSchema

from app.domains.train_job.repository.train_job import TrainJobRepository
from app.clients.rabbitmq_client import get_rabbitmq_client

from app.domains.train_job.schemas.train_job import TrainJobBody, TrainJobSchema
from app.domains.train_job.services.train_job import TrainJobService

logger = logging.getLogger(__name__) 


train_job_router = APIRouter(
    prefix='/api/v1',
    tags=["Train Jobs"]
)


@train_job_router.on_event("startup")
def on_train_job_router_startup():

    db_session = get_db_session()
    
    rabbitmq_client = get_rabbitmq_client()
    repository = TrainJobRepository(db_session)

    service = TrainJobService(repository)
    
    thread = threading.Thread(
        target=service.update_train_jobs_status, args=(rabbitmq_client,)
    )
    thread.setDaemon(True)
    thread.start()


@train_job_router.post("/train-jobs", response_model=TrainJobSchema)
async def add_train_job(
    train_job_body: TrainJobBody,
    
    db_session: Session = Depends(get_db_session),
    user: UserSchema = Depends(get_default_user)
) -> TrainJobSchema:   

    repository = TrainJobRepository(db_session)
    rabbitmq_client = get_rabbitmq_client()

    service = TrainJobService(repository)
    response = await service.add_train_job(train_job_body, user, rabbitmq_client)


    return response


@train_job_router.get("/train-jobs", response_model=list[TrainJobSchema])
def get_train_jobs(
    db_session: Session = Depends(get_db_session)
) -> TrainJobSchema:   

    repository = TrainJobRepository(db_session)

    service = TrainJobService(repository)
    response = service.get_train_jobs()


    return response


@train_job_router.delete("/train-jobs/{run_id}", response_model=bool)
def delete_train_job(
    run_id: uuid.UUID,
    db_session: Session = Depends(get_db_session)
) -> TrainJobSchema:   

    repository = TrainJobRepository(db_session)

    service = TrainJobService(repository)
    service.delete_train_job(run_id)


    return True
