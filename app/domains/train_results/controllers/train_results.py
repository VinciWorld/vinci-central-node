from io import BytesIO
import io
import json
import logging
import threading
import uuid
from fastapi.responses import StreamingResponse

from fastapi import APIRouter, Depends, File, UploadFile
from app.Auth.auth import auth
from app.clients.s3.interface import S3ClientInterface
from app.clients.s3.s3_client import get_s3_client
from app.db.connection import Session, get_db_session
from app.domains.core.repository.user_repository import get_default_user

from app.domains.core.schemas.user import UserSchema
from app.domains.train_job.repository.train_job import TrainJobRepository

from app.domains.train_job.schemas.train_job import  TrainJobSchema
from app.domains.train_results.services.train_results import TrainResultsService


logger = logging.getLogger(__name__) 


train_results_router = APIRouter(
    prefix='/api/v1',
    tags=["Train Results"]
)
   

@train_results_router.put("/train-jobs/{run_id}/nn-model", response_model=bool)
async def save_nn_model(
    run_id: uuid.UUID,
    nn_model: UploadFile = File(...),
    s3_client: S3ClientInterface = Depends(get_s3_client),
) -> TrainJobSchema:

    model_data = await nn_model.read()
    model_bytes = BytesIO(model_data)

    service = TrainResultsService(s3_client)
    response = await service.save_nn_mode(run_id, model_bytes)

    return response


@train_results_router.get("/train-jobs/{run_id}/nn-model")
async def get_user_train_nn_model(
    run_id: uuid.UUID,
    user: UserSchema = Depends(auth),
    db_session: Session = Depends(get_db_session),
    s3_client: S3ClientInterface = Depends(get_s3_client)
) -> StreamingResponse:
    
    train_job_repository = TrainJobRepository(db_session)

    service = TrainResultsService(s3_client)
    response = await service.get_user_train_nn_model(run_id, user.id, train_job_repository)

    return response


@train_results_router.get("/train-jobs/{run_id}/checkpoint")
async def get_user_train_checkpoint(
    run_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
    s3_client: S3ClientInterface = Depends(get_s3_client)
) -> StreamingResponse:
    
    train_job_repository = TrainJobRepository(db_session)

    service = TrainResultsService(s3_client)
    response = await service.get_user_train_checkpoint(run_id, train_job_repository)

    return response


@train_results_router.get("/train-jobs/{run_id}/train-results")
async def get_user_train_results(
    run_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
    s3_client: S3ClientInterface = Depends(get_s3_client),
    user: UserSchema = Depends(auth)
):
    train_job_repository = TrainJobRepository(db_session)

    service = TrainResultsService(s3_client)
    response = await service.get_user_train_results(run_id, user.id, train_job_repository)

    return response

@train_results_router.post("/train-jobs/{run_id}/results", response_model=bool)
async def save_train_results(
    run_id: uuid.UUID,
    results_zip: UploadFile = File(...),
    db_session: Session = Depends(get_db_session),
    s3_client: S3ClientInterface = Depends(get_s3_client),
) -> TrainJobSchema:

    repository = TrainJobRepository(db_session)

    service = TrainResultsService(s3_client)
    response = await service.save_train_results(run_id, results_zip, repository)

    return response