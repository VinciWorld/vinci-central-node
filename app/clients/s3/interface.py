from abc import ABC, abstractmethod
from typing import Tuple
from io import BytesIO
import uuid


class S3ClientInterface(ABC):

    @abstractmethod
    def get_nn_model(self, run_id: uuid.UUID, user_id: uuid.UUID) -> BytesIO:
        """Retrieve the nn_model."""
        pass
    
    @abstractmethod
    def put_nn_model(self, run_id: uuid.UUID, nn_model: BytesIO):
        pass

    @abstractmethod
    def extract_and_upload_zip_folder(self, run_id: uuid.UUID, zip_file: BytesIO):
        """Upload directory"""
        pass

    @abstractmethod
    def get_user_train_results(self, run_id: uuid.UUID, user_id: uuid.UUID) -> Tuple[BytesIO, BytesIO]:
        """Retrieve train model and checkpoint files"""
        pass

    @abstractmethod
    def get_model_checkpoint(self, run_id: uuid.UUID, user_id: uuid.UUID) -> BytesIO:
        """Retrieve train checkpoint file"""
        pass

    @abstractmethod
    def create_zip_from_folder(self, run_id: uuid.UUID, user_id: uuid.UUID) -> BytesIO:
        """Retrieve train folder"""
        pass

    @abstractmethod
    def extract_and_upload_zip_folder(
            self, run_id: uuid.UUID,
            zip_file: BytesIO,
            user_id: uuid.UUID
    ):
        """Extract zip and save"""
        pass