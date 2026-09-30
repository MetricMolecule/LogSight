import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://logsight:logsight@localhost:5432/logsight",
)


if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


# SQLAlchemy base used by app.models
Base = declarative_base()


# Database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


@contextmanager
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def init_db():

    Base.metadata.create_all(bind=engine)
