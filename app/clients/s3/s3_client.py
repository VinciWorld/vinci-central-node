from app.clients.s3.interface import S3ClientInterface
from app.clients.s3.s3_fake_client import S3FakeClient
from app.configuration.settings import Environments, settings


class S3Client(S3ClientInterface):
    def init(self, s3_client: any):
        self.s3_client = s3_client

        
    def upload_directory_to_s3(source_directory):
        """
        Uploads a directory to an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :param source_directory: Directory to upload.
        :param s3_client: Initialized boto3 S3 client.
        """
        for item in source_directory.iterdir():
            if item.is_file():
                file_key = f"{source_directory.name}/{item.name}"
                s3_client.upload_file(str(item), bucket_name, file_key)
            elif item.is_dir():
                upload_directory_to_s3(bucket_name, item, s3_client)


def get_s3_client() -> S3ClientInterface:
    if settings.env == Environments.LOCAL:
        aws_s3_client = None

        return S3FakeClient(aws_s3_client)
    
    else:
       # aws_s3_client = boto3.client(
       #     "s3",
       #     region_name="eu-west-1"
       # )

       return S3Client(None)
       pass



    