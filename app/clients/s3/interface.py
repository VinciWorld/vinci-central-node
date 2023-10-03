from abc import ABC, abstractmethod
from io import BytesIO
import uuid


class S3ClientInterface(ABC):

    @abstractmethod
    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        """Save the nn_model."""
        pass

    @abstractmethod
    def get_nn_model(self, run_id: uuid.UUID) -> BytesIO:
        """Retrieve the nn_model."""
        pass

    @abstractmethod
    def upload_file(self, run_id: uuid.UUID):
        """Upload file"""
        pass

    def upload_directory(self, run_id: uuid.UUID, source_directory: str):
        """Upload directory"""
        pass

    def extract_and_upload_zip_folder(self, run_id: uuid.UUID, zip_file: BytesIO):
        """Upload directory"""
        pass