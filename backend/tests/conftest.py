import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.database import SessionLocal


@pytest.fixture(scope="session")
def db_session():
    """Provides a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """Provides a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
