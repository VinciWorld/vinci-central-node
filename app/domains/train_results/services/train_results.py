
from functools import partial
from io import BytesIO
import json
import logging
import uuid
import zipfile

from anyio import Path
from fastapi import HTTPException

from app.clients.rabbitmq_client import RabbitMQClient
from app.clients.s3.interface import S3ClientInterface
from app.db.connection import Session, get_db_session
from app.domains.core.schemas.user import UserSchema
from app.domains.train_job.schemas.train_job import TrainJobBody, TrainJobCreate, TrainJobQueue, TrainJobSchema
from app.domains.train_job.schemas.train_job_constants import TrainJobStatus, TrainJobType
from app.settings.settings import settings

logger = logging.getLogger(__name__) 


class NNModelService():
    def __init__(self, s3_client: S3ClientInterface):
        self.s3_client = s3_client

    async def save_nn_mode(self, run_id: uuid.UUID, nn_model: BytesIO) -> bool:

        self.s3_client.put_nn_model(run_id, nn_model)

        return True
    
    async def save_train_results(self, run_id: uuid.UUID, results_zip: BytesIO):
        try:

            self.s3_client.extract_and_upload_zip_folder(run_id, results_zip)

            return True

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    




    

