from enum import Enum
from pathlib import Path
import ssl
import uuid
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from decouple import config

ENV: str = config('ENV', default="local")
NODE_ID: str = config('NODE_ID')
NODE_DOMAIN: str = config('NODE_DOMAIN')
FASTAPI_HOST: str = config('FASTAPI_HOST', default="127.0.0.1")
FASTAPI_PORT: int = config('FASTAPI_PORT', default=8000)
POSTGRES_USER: str = config('POSTGRES_USER')
POSTGRES_PASSWORD: str = config('POSTGRES_PASSWORD')
DB_HOST: str = config('DB_HOST')
DB_PORT: int = config('DB_PORT', default=5432, cast=int)
POSTGRES_DB: str = config('POSTGRES_DB')
RABBITMQ_USER=config('RABBITMQ_USER')
RABBITMQ_PASSWORD=config('RABBITMQ_PASSWORD')
RABBITMQ_HOST=config('RABBITMQ_HOST')
RABBITMQ_PORT=config('RABBITMQ_PORT')


ROOT_DIR = Path(__file__).parent.parent.parent

class Environments(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

class BaseConfig(BaseSettings):
    env: str = ENV
    root_dir: Path = ROOT_DIR
    node_id: uuid.UUID = NODE_ID
    node_domain: str = NODE_DOMAIN
    fastapi_host: str = FASTAPI_HOST
    fast_api_port: str = FASTAPI_PORT
    postgres_user: str = POSTGRES_USER
    postgres_password: str = POSTGRES_PASSWORD
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    postgres_db_name: str = POSTGRES_DB
    rabbitmq_user: str = RABBITMQ_USER
    rabbitmq_password: str = RABBITMQ_PASSWORD
    rabbitmq_host: str = RABBITMQ_HOST
    rabbitmq_port: str = RABBITMQ_PORT
    s3_bucket: str = "vinci-world-cloud-dev-central-node-bucket"

class DatabaseSettings(BaseConfig):
    @property
    def db_url(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.db_host,
            port=self.db_port,
            path=self.postgres_db_name
        )

class LocalSettings(DatabaseSettings):
    pass

class DevSettings(DatabaseSettings):
    pass

if ENV == Environments.LOCAL.value:
    settings = LocalSettings()
elif ENV == Environments.DEV.value:
    settings = DevSettings()
else:
    raise ValueError(f"Unsupported environment: {ENV}")

class RabbitMQClientSettings():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
    url = f"amqps://{settings.rabbitmq_user}:{settings.rabbitmq_password}@{settings.rabbitmq_host}:{settings.rabbitmq_port}"

    class Confg:
        env_file_encoding= "utf-8"

rabbitmq_settings = RabbitMQClientSettings()
