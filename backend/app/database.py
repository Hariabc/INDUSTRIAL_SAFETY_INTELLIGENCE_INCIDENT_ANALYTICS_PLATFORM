from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings


def utcnow():
    """Return naive UTC datetime for database column defaults (replaces deprecated datetime.utcnow)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

database_url = settings.DATABASE_URL

# Handle SQLite vs Postgres connection arguments
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
