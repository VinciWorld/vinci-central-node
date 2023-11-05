from io import BytesIO
import logging
import uuid
import boto3
from app.clients.s3.interface import S3ClientInterface
from app.clients.s3.s3_fake_client import S3FakeClient
from app.settings.settings import Environments, settings

logger = logging.getLogger(__name__) 

class S3Client(S3ClientInterface):
    def __init__(self, s3_client: any):
        self.s3_client = s3_client
        self.bucket_name = settings.s3_bucket

    def _get_model_path(self, run_id: uuid.UUID) -> str:
        return f"runs/{str(run_id)}/models"

    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        model_path = f"{self._get_model_path(run_id)}/model.onnx"
        try:
            self.s3_client.upload_fileobj(nn_model, self.bucket_name, model_path)
        except Exception:
            print("Credentials not available")

    def get_nn_model(self, run_id: uuid.UUID) -> BytesIO:

        model_path = f"{self._get_model_path(run_id)}/model.onnx"
        nn_model = BytesIO()
        try:
            self.s3_client.download_fileobj(self.bucket_name, model_path, nn_model)
            nn_model.seek(0)
        except Exception:
            logger.info("Unable to get model run_id: " + run_id)

        return nn_model
    
    def extract_and_upload_zip_folder(self, run_id: uuid.UUID, zip_file: BytesIO):
        """Upload directory"""
        pass


def get_s3_client() -> S3ClientInterface:
    if settings.env == Environments.LOCAL:
        aws_s3_client = None
        return S3FakeClient(aws_s3_client)
    else:
        aws_s3_client = boto3.client('s3')

        return S3Client(aws_s3_client)





    