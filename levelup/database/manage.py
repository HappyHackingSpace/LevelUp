import logging

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import Engine
from sqlalchemy.schema import CreateSchema, Table
from sqlalchemy_utils import create_database, database_exists

import levelup.config as config

from .core import Base

log = logging.getLogger(__file__)


def version_schema(script_location: str) -> None:
    """Applies alembic versioning to schema."""
    try:
        # add it to alembic table
        alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("script_location", script_location)
        alembic_command.stamp(alembic_cfg, "head")
    except Exception as e:
        log.warning(f"Could not stamp alembic schema: {e}")


def get_core_tables() -> list[Table]:
    """Fetches tables that belong to the 'dispatch_core' schema."""
    core_tables: list[Table] = []
    for _, table in Base.metadata.tables.items():
        if table.schema == "dispatch_core":
            core_tables.append(table)
    return core_tables


def get_tenant_tables() -> list[Table]:
    """Fetches tables that belong to their own tenant tables."""
    tenant_tables: list[Table] = []
    for _, table in Base.metadata.tables.items():
        if not table.schema:
            tenant_tables.append(table)
    return tenant_tables


def init_database(engine: Engine) -> None:
    """Initializes the database."""
    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        create_database(str(config.SQLALCHEMY_DATABASE_URI))

    schema_name = "dispatch_core"
    with engine.begin() as connection:
        connection.execute(CreateSchema(schema_name, if_not_exists=True))

    tables = get_core_tables()

    Base.metadata.create_all(engine, tables=tables)

    version_schema(script_location=config.ALEMBIC_CORE_REVISION_PATH)

    # setup any required database functions if needed
    # TODO: Add any database initialization functions here

    log.info("Database initialized successfully")
