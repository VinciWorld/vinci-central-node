from io import BytesIO
import io
import logging
import threading
import uuid
from fastapi.responses import StreamingResponse

from fastapi import APIRouter, Depends, File, UploadFile
from app.clients.s3.interface import S3ClientInterface
from app.clients.s3.s3_client import get_s3_client

from app.domains.core.models.user import get_default_user
from app.domains.core.schemas.user import UserSchema

from app.domains.train_job.schemas.train_job import  TrainJobSchema
from app.domains.train_results.services.train_results import NNModelService


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
    user: UserSchema = Depends(get_default_user)
) -> TrainJobSchema:

    model_data = await nn_model.read()
    model_bytes = BytesIO(model_data)

    service = NNModelService(s3_client)
    response = await service.save_nn_mode(run_id, model_bytes)

    return response


@train_results_router.get("/train-jobs/{run_id}/nn-model", response_model=list[TrainJobSchema])
async def get_nn_model(
    run_id: uuid.UUID,
    s3_client: S3ClientInterface = Depends(get_s3_client)
) -> StreamingResponse:
    
    model_bytes = s3_client.get_nn_model(run_id)
    
    model_data = model_bytes.getvalue()

    return StreamingResponse(io.BytesIO(model_data), media_type="application/octet-stream", headers={
        "Content-Disposition": f"attachment; filename=model_{run_id}.onnx"
    })


@train_results_router.put("/train-jobs/{run_id}/results", response_model=bool)
async def save_train_results(
    run_id: uuid.UUID,
    results_zip: UploadFile = File(...),
    s3_client: S3ClientInterface = Depends(get_s3_client),
    user: UserSchema = Depends(get_default_user)
) -> TrainJobSchema:

    results_zip_data = await results_zip.read()
    results_zip_bytes = BytesIO(results_zip_data)

    service = NNModelService(s3_client)
    response = await service.save_train_results(run_id, results_zip_bytes)

    return response