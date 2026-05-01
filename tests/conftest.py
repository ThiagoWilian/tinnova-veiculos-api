from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Base
from app.models.user import UserRole
from app.repositories.user_repository import user_repository
from app.services.cotacao_service import cotacao_service


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        user_repository.create(db, "admin@test.com", "admin123", UserRole.ADMIN)
        user_repository.create(db, "user@test.com", "user123", UserRole.USER)
        yield db

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def fixed_cotacao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cotacao_service, "usd_brl", lambda: Decimal("5.00"))


@pytest.fixture
def client(db_session: Session, fixed_cotacao: None) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "user123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def veiculo_payload() -> dict[str, object]:
    return {
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2022,
        "cor": "Prata",
        "placa": "ABC1D23",
        "preco_brl": "100000.00",
    }
