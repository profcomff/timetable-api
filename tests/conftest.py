from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette import status

from calendar_backend.models.base import DeclarativeBase
from calendar_backend.models.db import Event, Group, Lecturer, Room
from calendar_backend.routes import app
from calendar_backend.settings import get_settings
from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from alembic.config import Config as AlembicConfig
from pathlib import Path
from testcontainers.postgres import PostgresContainer


class PostgresConfig:
    """Дата-класс со значениями для контейнера с тестовой БД и для alembic-миграции."""

    container_name: str = "modal-service-api_test"
    username: str = "postgres"
    host: str = "localhost"
    external_port: int = 5432
    image: str = "postgres:15"
    host_auth_method: str = "trust"
    alembic_ini: str = Path(__file__).resolve().parent.parent / "alembic.ini"

    @classmethod
    def get_url(cls) -> str:
        """Возвращает URI для подключения к БД."""
        return f"postgresql://{cls.username}@{cls.host}:{cls.external_port}/postgres"



@pytest.fixture(scope="session")
def db_container():
    """Фикстура настройки БД для тестов в Docker-контейнере."""
    container = (
        PostgresContainer(
            image=PostgresConfig.image, username=PostgresConfig.username, dbname=PostgresConfig.container_name
        )
        .with_bind_ports(5432, PostgresConfig.external_port)
        .with_env("POSTGRES_HOST_AUTH_METHOD", PostgresConfig.host_auth_method)
    )
    container.start()
    alembic_ini = PostgresConfig.alembic_ini
    cfg = AlembicConfig(str(alembic_ini.resolve()))
    cfg.set_main_option("script_location", "%(here)s/migrations")
    command.upgrade(cfg, "head")
    try:
        yield PostgresConfig.get_url()
    finally:
        container.stop()


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def client_auth(mocker: MockerFixture):
    user_mock = mocker.patch('auth_lib.fastapi.UnionAuth.__call__', autospec=True)
    user_mock.return_value = {
        "session_scopes": [{"id": 0, "name": "string", "comment": "string"}],
        "user_scopes": [{"id": 0, "name": "string", "comment": "string"}],
        "indirect_groups": [{"id": 0, "name": "string", "parent_id": 0}],
        "groups": [{"id": 0, "name": "string", "parent_id": 0}],
        "id": 0,
        "email": "string",
    }
    client = TestClient(app)
    return client


@pytest.fixture()
def dbsession(db_container):
    engine = create_engine(str(db_container), isolation_level='AUTOCOMMIT')
    TestingSessionLocal = sessionmaker(bind=engine)
    DeclarativeBase.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.fixture()
def room_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/room/"
    request_obj = {
        "name": datetime.now().isoformat(),
        "direction": "North",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model: Room = dbsession.query(Room).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def group_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/group/"
    request_obj = {
        "name": "",
        "number": datetime.now().isoformat(),
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model: Group = dbsession.query(Group).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def lecturer_path(client_auth: TestClient, dbsession: Session):
    RESOURCE = "/lecturer/"
    request_obj = {
        "first_name": "Петр",
        "middle_name": "Васильевич",
        "last_name": "Тритий",
        "description": "Очень умный",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    assert response.status_code == status.HTTP_200_OK, response.json()
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model: Lecturer = dbsession.query(Lecturer).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def event_path(client_auth: TestClient, dbsession: Session, lecturer_path, room_path, group_path):
    RESOURCE = f"/event/"
    room_id = int(room_path.split("/")[-1])
    group_id = int(group_path.split("/")[-1])
    lecturer_id = int(lecturer_path.split("/")[-1])
    request_obj = {
        "name": "string",
        "room_id": [room_id],
        "group_id": [group_id],
        "lecturer_id": [lecturer_id],
        "start_ts": "2022-08-26T22:32:38.575Z",
        "end_ts": "2022-08-26T22:32:38.575Z",
    }
    response = client_auth.post(RESOURCE, json=request_obj)
    id_ = response.json()["id"]
    yield RESOURCE + str(id_)
    response_model = dbsession.query(Event).get(id_)
    dbsession.delete(response_model)
    dbsession.commit()


@pytest.fixture()
def room_factory(dbsession: Session):
    ids_ = []

    def _room_factory(client_auth: TestClient):
        RESOURCE = "/room/"
        request_obj = {
            "name": datetime.now().isoformat(),
            "direction": "North",
        }
        response = client_auth.post(RESOURCE, json=request_obj)
        assert response.status_code == status.HTTP_200_OK, response.json()
        nonlocal ids_
        ids_.append(yielding := response.json()["id"])
        return RESOURCE + str(yielding)

    yield _room_factory
    for id in ids_:
        response_model: Room = dbsession.query(Room).get(id)
        dbsession.delete(response_model)
        dbsession.commit()


@pytest.fixture()
def lecturer_factory(dbsession: Session):
    ids_ = []

    def _lecturer_factory(client_auth: TestClient):
        RESOURCE = "/lecturer/"
        request_obj = {
            "first_name": "Петр",
            "middle_name": "Васильевич",
            "last_name": "Тритий",
            "description": "Очень умный",
        }
        response = client_auth.post(RESOURCE, json=request_obj)
        assert response.status_code == status.HTTP_200_OK, response.json()
        nonlocal ids_
        ids_.append(yielding := response.json()["id"])
        return RESOURCE + str(yielding)

    yield _lecturer_factory
    for id in ids_:
        response_model: Lecturer = dbsession.query(Lecturer).get(id)
        dbsession.delete(response_model)
        dbsession.commit()


@pytest.fixture()
def group_factory(dbsession: Session):
    ids_ = []

    def _group_factory(client_auth: TestClient):
        RESOURCE = "/group/"
        request_obj = {
            "name": "",
            "number": datetime.now().isoformat(),
        }
        response = client_auth.post(RESOURCE, json=request_obj)
        assert response.status_code == status.HTTP_200_OK, response.json()
        nonlocal ids_
        ids_.append(yielding := response.json()["id"])
        return RESOURCE + str(yielding)

    yield _group_factory
    for id in ids_:
        response_model: Group = dbsession.query(Group).get(id)
        dbsession.delete(response_model)
        dbsession.commit()
