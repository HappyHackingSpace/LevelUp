import logging
import os
from urllib import parse

from pydantic import BaseModel
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

logger = logging.getLogger(__name__)


class Secret:
    """
    Holds a string value that should not be revealed in tracebacks etc.
    Just returns the value as-is for now.
    """

    def __init__(self, value: str):
        self._value = value

    def __repr__(self) -> str:
        return "Secret('**********')"

    def __str__(self) -> str:
        return self._value


class BaseConfigurationModel(BaseModel):
    pass


def get_env_tags(tag_list: list[str]) -> dict:
    """Create dictionary of available env tags."""
    tags = {}
    for t in tag_list:
        tag_key, env_key = t.split(":")

        env_value = os.environ.get(env_key)

        if env_value:
            tags.update({tag_key: env_value})

    return tags


config = Config(".env")


LOG_LEVEL: int = config("LOG_LEVEL", default=logging.WARNING)
ENV: str = config("ENV", default="local")

# FastAPI settings
PROJECT_NAME = config("PROJECT_NAME", default="LevelUP")
API_V1_STR = config("API_V1_STR", default="/api/v1")

# CORS settings
BACKEND_CORS_ORIGINS = config(
    "BACKEND_CORS_ORIGINS",
    cast=CommaSeparatedStrings,
    default="http://localhost:8000,http://localhost:3000",
)
all_cors_origins = [str(origin) for origin in BACKEND_CORS_ORIGINS]

# sentry middleware
SENTRY_DSN = config("SENTRY_DSN", default="")
SENTRY_APP_KEY = config("SENTRY_APP_KEY", default="")
SENTRY_TAGS = config("SENTRY_TAGS", default="")

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME", default="localhost")
DATABASE_CREDENTIALS = config(
    "DATABASE_CREDENTIALS", cast=Secret, default="user:password"
)
# this will support special chars for credentials
_DATABASE_CREDENTIAL_USER, _DATABASE_CREDENTIAL_PASSWORD = str(
    DATABASE_CREDENTIALS
).split(":")
_QUOTED_DATABASE_PASSWORD = parse.quote(str(_DATABASE_CREDENTIAL_PASSWORD))
DATABASE_NAME = config("DATABASE_NAME", default="dispatch")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
DATABASE_ENGINE_MAX_OVERFLOW = config(
    "DATABASE_ENGINE_MAX_OVERFLOW", cast=int, default=10
)
# Deal with DB disconnects
# https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
DATABASE_ENGINE_POOL_PING: bool = config("DATABASE_ENGINE_POOL_PING", default=False)
DATABASE_ENGINE_POOL_RECYCLE = config(
    "DATABASE_ENGINE_POOL_RECYCLE", cast=int, default=3600
)
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=20)
DATABASE_ENGINE_POOL_TIMEOUT = config(
    "DATABASE_ENGINE_POOL_TIMEOUT", cast=int, default=30
)
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{_DATABASE_CREDENTIAL_USER}:{_QUOTED_DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

ALEMBIC_CORE_REVISION_PATH = config(
    "ALEMBIC_CORE_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database/alembic",
)
ALEMBIC_INI_PATH = config(
    "ALEMBIC_INI_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/alembic.ini",
)

GEMINI_API_KEY = config("GEMINI_API_KEY", default="", cast=str)
