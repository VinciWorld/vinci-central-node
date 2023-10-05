from io import BytesIO
from pathlib import Path
import uuid
import zipfile
from app.clients.s3.interface import S3ClientInterface
from app.settings.settings import settings


class S3FakeClient(S3ClientInterface):
    def __init__(self, s3_client: any):
        self.bucket_path = settings.root_dir / "fake_s3"

    def _get_model_path(self, run_id: uuid.UUID) -> Path:

        return self.bucket_path / "runs" / str(run_id) / "models"

    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        model_path = self._get_model_path(run_id)
        model_path.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

        with open(model_path / "model.onnx", "wb") as f:
            f.write(nn_model.getvalue())

    def get_nn_model(self, run_id: uuid.UUID) -> BytesIO:
        model_path = self._get_model_path(run_id) / "model.onnx"
        
        if not model_path.exists():
            raise FileNotFoundError(f"No model found for run_id: {run_id}")

        with open(model_path, "rb") as f:
            return BytesIO(f.read())

    def extract_and_upload_zip_folder(self, run_id: uuid.UUID, zip_file: BytesIO):
        with zipfile.ZipFile(zip_file) as zf:

            output_path = self.bucket_path / "runs " / Path(str(run_id))
            output_path.mkdir(parents=True, exist_ok=True)

            zf.extractall(output_path)


    def upload_directory(self, run_id: uuid.UUID, source_directory: str):
        """Upload directory"""
        pass

