from abc import ABC, abstractmethod
from io import BytesIO
import uuid


class S3ClientInterface(ABC):

    @abstractmethod
    def get_nn_model(self, run_id: uuid.UUID) -> BytesIO:
        """Retrieve the nn_model."""
        pass
    
    @abstractmethod
    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        pass

    @abstractmethod
    def extract_and_upload_zip_folder(self, run_id: uuid.UUID, zip_file: BytesIO):
        """Upload directory"""
        pass