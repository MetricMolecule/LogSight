from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/logsight"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
