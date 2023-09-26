from enum import Enum
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from decouple import config


ENV: str = config('ENV', default="local")
POSTGRES_USER: str = config('POSTGRES_USER')
POSTGRES_PASSWORD: str = config('POSTGRES_PASSWORD')
DB_HOST: str = config('DB_HOST')
DB_PORT: int = config('DB_PORT', default=5432, cast=int)
POSTGRES_DB: str = config('POSTGRES_DB')


class Environments(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

class BaseConfig(BaseSettings):
    env: str = ENV

    postgres_user: str = POSTGRES_USER
    postgres_password: str = POSTGRES_PASSWORD
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    postgres_db_name: str = POSTGRES_DB


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