from datetime import datetime
from io import BytesIO
import logging
from pathlib import Path
import shutil
from typing import Tuple
import uuid
import zipfile
from app.clients.s3.interface import S3ClientInterface
from app.settings.settings import settings

logger = logging.getLogger(__name__) 

class S3FakeClient(S3ClientInterface):
    def __init__(self, s3_client: any):
        self.bucket_path = settings.root_dir / "fake_s3"

    def _get_run_path(self, run_id: uuid.UUID) -> Path:

        return self.bucket_path / "runs" / str(run_id)

    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        model_path = self._get_run_path(run_id)

        model_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"nnmodel path: {model_path}")

        with open(model_path / "model.onnx", "wb") as f:
            f.write(nn_model.getvalue())

    def get_nn_model(self, run_id: uuid.UUID, user_id: uuid.UUID) -> BytesIO:
        recent_folder = self._get_most_recent_folder(run_id, user_id)
        model_path = recent_folder / "model.onnx"
        
        if not model_path.exists():
            raise FileNotFoundError(f"No model found for run_id: {run_id}")

        with open(model_path, "rb") as f:
            return BytesIO(f.read())
        
        
    def get_user_train_results(self, run_id: uuid.UUID, user_id: uuid.UUID) -> Tuple[BytesIO, BytesIO]:
        recent_folder = self._get_most_recent_folder(run_id, user_id)
        model_path = recent_folder / "model.onnx"
        metrics_path = recent_folder / "metrics.json"

        if not model_path.exists() or not metrics_path.exists():
            raise FileNotFoundError(f"No model or metrics found for run_id: {run_id}")

        with open(model_path, "rb") as model_file, open(metrics_path, "rb") as metrics_file:
            model_data = BytesIO(model_file.read())
            metrics_data = BytesIO(metrics_file.read())

        return model_data, metrics_data
        
    def get_model_checkpoint(self, run_id: uuid.UUID, user_id: uuid.UUID) -> BytesIO:
        recent_folder = self._get_most_recent_folder(run_id, user_id)
        checkpoint_path = recent_folder / "checkpoint.pt"
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"No checkpoint found for run_id: {run_id}")

        with open(checkpoint_path, "rb") as f:
            return BytesIO(f.read())

    def create_zip_from_folder(self, run_id: uuid.UUID, user_id: uuid.UUID) -> BytesIO:

        zip_buffer = BytesIO()
        output_path = self.bucket_path / "runs" / Path(str(user_id)) /  Path(str(run_id))

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in output_path.rglob('*'):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(output_path))

        zip_buffer.seek(0)
        return zip_buffer

    def extract_and_upload_zip_folder(
            self, run_id: uuid.UUID,
            zip_file: BytesIO,
            user_id: uuid.UUID
    ):
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.bucket_path / "runs" / Path(str(user_id)) / Path(str(run_id)) / current_datetime
        output_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_file) as zf:
            for member in zf.infolist():
                # Extract only if it's a file (not a directory)
                if not member.is_dir():
                    # Get the target path (without the zip's root directory)
                    target_path = output_path / Path(*Path(member.filename).parts[1:])
                    # Make sure the target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    # Extract the file to the target path
                    with zf.open(member, 'r') as source, open(target_path, 'wb') as target:
                        target.write(source.read())

        #TODO: activate this in the future
        runs_path = self.bucket_path / "runs" / Path(str(user_id)) / Path(str(run_id))
        clean_and_keep_recent_folders(runs_path)


    def _get_most_recent_folder(self, run_id: uuid.UUID, user_id: uuid.UUID) -> Path:
        base_path = self.bucket_path / "runs" / Path(str(user_id)) / Path(str(run_id))
        all_subdirs = [d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if not all_subdirs:
            raise FileNotFoundError(f"No data found for run_id: {run_id}")
        latest_subdir = max(all_subdirs, key=lambda d: datetime.strptime(d.name, "%Y%m%d_%H%M%S"))
        return latest_subdir
    

def clean_and_keep_recent_folders(parent_path: Path, max_folders: int = 2):
    all_subdirs = [subdir for subdir in parent_path.iterdir() if subdir.is_dir()]
    
    sorted_subdirs = sorted(all_subdirs, key=lambda d: d.stat().st_mtime, reverse=True)
    
    for subdir in sorted_subdirs[max_folders:]:
        shutil.rmtree(subdir)
