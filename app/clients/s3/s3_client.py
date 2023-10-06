from io import BytesIO
import uuid
from app.clients.s3.interface import S3ClientInterface
from app.clients.s3.s3_fake_client import S3FakeClient
from app.settings.settings import Environments, settings


class S3Client(S3ClientInterface):
    def init(self, s3_client: any):
        self.s3_client = s3_client

    def _get_model_path(self, run_id: uuid.UUID) -> str:
        return f"runs/{str(run_id)}/models"

    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        model_path = f"{self._get_model_path(run_id)}/model.onnx"
        try:
            self.s3_client.upload_fileobj(nn_model, self.bucket_name, model_path)
        except NoCredentialsError:
            print("Credentials not available")

    def get_nn_model(self, run_id: uuid.UUID) -> BytesIO:
        model_path = f"{self._get_model_path(run_id)}/model.onnx"
        nn_model = BytesIO()
        self.s3_client.download_fileobj(self.bucket_name, model_path, nn_model)
        nn_model.seek(0)
        return nn_model


def get_s3_client() -> S3ClientInterface:
    if settings.env == Environments.LOCAL:
        aws_s3_client = None
        return S3FakeClient(aws_s3_client)
    else:
       pass
       # aws_s3_client = boto3.client('s3')





    