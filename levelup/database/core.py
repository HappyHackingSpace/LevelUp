import functools
import logging
import re
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, Session, declared_attr, sessionmaker
from starlette.requests import Request

import levelup.config as cfg

logger = logging.getLogger(__name__)


class SessionTracker:
    """Stub implementation for session tracking."""

    _sessions: dict[str, dict[str, Any]] = {}

    @classmethod
    def track_session(cls, session: Session, context: str | None = None) -> str:
        """Tracks a new database session."""
        session_id = str(uuid.uuid4())
        cls._sessions[session_id] = {
            "session": session,
            "context": context,
            "created_at": datetime.now().timestamp(),
        }
        logger.info(
            "Database session created",
            extra={
                "session_id": session_id,
                "context": context,
                "total_active_sessions": len(cls._sessions),
            },
        )
        return session_id

    @classmethod
    def untrack_session(cls, session_id: str) -> None:
        """Untracks a database session."""
        if session_id in cls._sessions:
            session_info = cls._sessions.pop(session_id)
            duration = datetime.now().timestamp() - session_info["created_at"]
            logger.info(
                "Database session closed",
                extra={
                    "session_id": session_id,
                    "context": session_info["context"],
                    "duration_seconds": duration,
                    "total_active_sessions": len(cls._sessions),
                },
            )

    @classmethod
    def get_active_sessions(cls) -> list[dict[str, Any]]:
        """Returns information about all active sessions."""
        current_time = datetime.now().timestamp()
        return [
            {
                "session_id": session_id,
                "context": info["context"],
                "age_seconds": current_time - info["created_at"],
            }
            for session_id, info in cls._sessions.items()
        ]


def create_db_engine(connection_string: str) -> Any:
    """Create a database engine with proper timeout settings.

    Args:
        connection_string: Database connection string
    """
    url = make_url(connection_string)

    # Use existing configuration values with fallbacks
    timeout_kwargs = {
        # Connection timeout - how long to wait for a connection from the pool
        "pool_timeout": cfg.DATABASE_ENGINE_POOL_TIMEOUT,
        # Recycle connections after this many seconds
        "pool_recycle": cfg.DATABASE_ENGINE_POOL_RECYCLE,
        # Maximum number of connections to keep in the pool
        "pool_size": cfg.DATABASE_ENGINE_POOL_SIZE,
        # Maximum overflow connections allowed beyond pool_size
        "max_overflow": cfg.DATABASE_ENGINE_MAX_OVERFLOW,
        # Connection pre-ping to verify connection is still alive
        "pool_pre_ping": cfg.DATABASE_ENGINE_POOL_PING,
    }
    return create_engine(url, **timeout_kwargs)


# Create the default engine with standard timeout
engine = create_db_engine(
    cfg.SQLALCHEMY_DATABASE_URI,
)

# Enable query timing logging
#
# Set up logging for query debugging
# logger = logging.getLogger(__name__)
#
# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     conn.info.setdefault("query_start_time", []).append(time.time())
#     logger.debug("Start Query: %s", statement)

# @event.listens_for(Engine, "after_cursor_execute")
# def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     total = time.time() - conn.info["query_start_time"].pop(-1)
#     logger.debug("Query Complete!")
#     logger.debug("Total Time: %f", total)
#     # Log queries that take more than 1 second as warnings
#     if total > 1.0:
#         logger.warning("Slow Query (%.2fs): %s", total, statement)


SessionLocal = sessionmaker(bind=engine)


def resolve_table_name(name: str) -> str:
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


raise_attribute_error = object()


def resolve_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Attempts to access attr via dotted notation, returns none if attr does not exist."""
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return default


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    __repr_attrs__: list[str] = []
    __repr_max_length__: int = 15

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return resolve_table_name(cls.__name__)

    def dict(self) -> dict[str, Any]:
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self) -> str:
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self) -> str:
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in __repr__attrs__".format(
                        self.__class__, key
                    )
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self) -> str:
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )


def get_db(request: Request) -> Any:
    """Get database session from request state."""
    session = request.state.db
    if not hasattr(session, "_dispatch_session_id"):
        setattr(
            session,
            "_dispatch_session_id",
            SessionTracker.track_session(session, context="fastapi_request"),
        )
    return session


DbSession = Annotated[Session, Depends(get_db)]


def get_model_name_by_tablename(table_fullname: str) -> Any:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""

    def _find_class(name: str) -> Any:
        for mapper in Base.registry.mappers:
            cls = mapper.class_
            if hasattr(cls, "__table__"):
                if cls.__table__.fullname.lower() == name.lower():
                    return cls

    mapped_name = resolve_table_name(table_fullname)
    mapped_class = _find_class(mapped_name)

    # try looking in the 'dispatch_core' schema
    if not mapped_class:
        mapped_class = _find_class(f"dispatch_core.{mapped_name}")

    if not mapped_class:
        raise ValueError(
            f"Model not found for table '{table_fullname}'. "
            "Check the name of your model."
        )

    return mapped_class


def get_table_name_by_class_instance(class_instance: Base) -> str:
    """Returns the name of the table for a given class instance."""
    return inspect(class_instance).mapper.mapped_table.name  # type: ignore


def refetch_db_session(organization_slug: str) -> Session:
    """Create a new database session for a specific organization."""
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{organization_slug}",
        }
    )
    session = sessionmaker(bind=schema_engine)()
    session._dispatch_session_id = SessionTracker.track_session(  # type: ignore
        session, context=f"organization_{organization_slug}"
    )
    return session


@contextmanager
def get_session() -> Generator[Session, Any, None]:
    """Context manager to ensure the session is closed after use."""
    session = SessionLocal()
    session_id = SessionTracker.track_session(session, context="context_manager")
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        SessionTracker.untrack_session(session_id)
        session.close()
