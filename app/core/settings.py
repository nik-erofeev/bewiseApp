import os
from enum import StrEnum, unique

from pydantic import BaseModel, computed_field, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


@unique
class Environments(StrEnum):
    local = "local"
    qa = "qa"
    stage = "stage"
    prod = "prod"
    test = "test"


class DbConfig(BaseModel):
    user: str = ""
    password: str = ""
    host: str = ""
    port: int = 5432
    name: str = ""

    max_size: int = 1
    echo: bool = True

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_db_uri(self) -> PostgresDsn:
        multi_host_url = MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.name,
        )

        return PostgresDsn(str(multi_host_url))

    test_user: str = ""
    test_password: str = ""
    test_host: str = ""
    test_port: int = 15432
    test_name: str = ""  # postgres -тестовая

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_test_db_uri(self) -> PostgresDsn:
        multi_host_url = MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.test_user,
            password=self.test_password,
            host=self.test_host,
            port=self.test_port,
            path=self.test_name,
        )
        return PostgresDsn(str(multi_host_url))


class KafkaConfig(BaseModel):
    host: str = ""
    port: int = 9092
    topik: str = "default"

    @property
    def bootstrap_servers(self) -> str:
        return f"{self.host}:{self.port}"


class RedisConfig(BaseModel):
    host: str = ""


class Api(BaseModel):
    project_name: str = "BewiseApp"
    description: str = "BewiseApp API 🚀"
    version: str = "1.0.0"
    openapi_url: str = "/api/v1/openapi.json"
    echo: bool = False
    v1: str = "/v1"


class AppConfig(BaseSettings):
    db: DbConfig = DbConfig()
    redis: RedisConfig = RedisConfig()
    kafka: KafkaConfig = KafkaConfig()  # producer
    environment: Environments = Environments.local
    api: Api = Api()

    cors_origin_regex: str = r"(http://|https://)?(.*\.)?(qa|stage|localhost|0.0.0.0)(\.ru)?(:\d+)?$"

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    _ENV_FILES: list[str] = [
        f"{BASE_DIR}/.env.local.base",
        f"{BASE_DIR}/.env.local",
        f"{BASE_DIR}/.env",  # последний перезапишет
    ]

    download_dir: str = os.path.join(BASE_DIR, "app/static")

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        env_file=_ENV_FILES,
        # env_file=(f"{BASE_DIR}/.env2", f"{BASE_DIR}/.env.local", f"{BASE_DIR}/.env"),
    )


APP_CONFIG = AppConfig()
