from io import BytesIO
import io
import logging
import uuid

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from app.clients.s3.interface import S3ClientInterface
from app.domains.train_job.repository.train_job import TrainJobRepository

logger = logging.getLogger(__name__) 


class TrainResultsService():
    def __init__(self, s3_client: S3ClientInterface):
        self.s3_client = s3_client

    async def save_nn_mode(self, run_id: uuid.UUID, nn_model: BytesIO) -> bool:

        self.s3_client.put_nn_model(run_id, nn_model)

        return True
    

    async def get_user_train_nn_model(
        self,
        run_id: uuid.UUID,
        user_id: uuid.UUID,
        train_job_repository: TrainJobRepository 
    ) -> StreamingResponse:

        train_job_db = train_job_repository.get_by_run_id(run_id)
        if train_job_db is None:
            raise HTTPException(status_code=404, detail=str(f"train job with run id: {run_id}, Not Found"))
        elif train_job_db.created_by.id != user_id:
            raise HTTPException(
                status_code=403,
                detail=str(f"Train job with run id: {run_id}, don't belong to user: {user_id}")
            )
        

        model_bytes = self.s3_client.get_nn_model(run_id, user_id)
        model_data = model_bytes.getvalue()

        return StreamingResponse(
            io.BytesIO(model_data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=model.onnx"
            }       
        )

    
    async def get_user_train_checkpoint(
        self,
        run_id: uuid.UUID,
        user_id: uuid.UUID,
        train_job_repository: TrainJobRepository
    ) -> StreamingResponse:
        try:

            train_job_db = train_job_repository.get_by_run_id(run_id)
            if train_job_db is None:
                raise HTTPException(status_code=404, detail=str(f"train job with run id: {run_id}, Not Found"))
            elif train_job_db.created_by.id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail=str(f"Train job with run id: {run_id}, don't belong to user: {user_id}")
                )
            
            checkpoint_bytes = self.s3_client.get_model_checkpoint(run_id, user_id)
            checkpoint_data = checkpoint_bytes.getvalue()

            return StreamingResponse(
                io.BytesIO(checkpoint_data),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename=checkpoint.pt"
                }       
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_user_train_results(
            self,
            run_id: uuid.UUID,
            user_id: uuid.UUID,
            train_job_repository: TrainJobRepository ) -> StreamingResponse:
        try:

            train_job_db = train_job_repository.get_by_run_id(run_id)
            if train_job_db is None:
                raise HTTPException(status_code=404, detail=str(f"train job with run id: {run_id}, Not Found"))
            elif train_job_db.created_by.id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail=str(f"Train job with run id: {run_id}, don't belong to user: {user_id}")
                )
            
            model_bytes, metrics_bytes = self.s3_client.get_user_train_results(run_id, user_id)
    
            boundary = "Boundary-" + str(uuid.uuid4())
            headers = {
                "Content-Type": f"multipart/mixed; boundary={boundary}"
            }

            def content_generator():
                yield f"--{boundary}\r\n"
                yield f"Content-Disposition: form-data; name=model; filename=model_{run_id}.onnx\r\n"
                yield f"Content-Type: application/octet-stream\r\n\r\n"
                yield model_bytes.getvalue()
                yield f"\r\n--{boundary}\r\n"
                yield f"Content-Disposition: form-data; name=metrics; filename=metrics_{run_id}.json\r\n"
                yield f"Content-Type: application/json\r\n\r\n"
                yield metrics_bytes.getvalue()
                yield f"\r\n--{boundary}--"

            return StreamingResponse(content_generator(), headers=headers)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def save_train_results(
            self,
            run_id: uuid.UUID,
            results_zip: UploadFile,
            train_job_repository: TrainJobRepository
    ):

        train_job_db = train_job_repository.get_by_run_id(run_id)

        if train_job_db is None:
            raise HTTPException(status_code=404, detail=str(f"train job with run id: {run_id}, Not Found"))

        results_zip_data = await results_zip.read()
        results_zip_bytes = BytesIO(results_zip_data)

        self.s3_client.extract_and_upload_zip_folder(
            run_id,
            results_zip_bytes,
            train_job_db.created_by.id
        )

        return True
    
    




    

