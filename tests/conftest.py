import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from calendar_backend.models.base import Base
from calendar_backend.routes import app
from calendar_backend.settings import get_settings


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def client_auth(mocker: MockerFixture):
    client = TestClient(app)
    access_token = client.post(f"/token", {"username": "admin", "password": "42"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client


@pytest.fixture()
def dbsession():
    settings = get_settings()
    engine = create_engine(settings.DB_DSN)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()
