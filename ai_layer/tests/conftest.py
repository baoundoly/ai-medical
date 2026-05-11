"""
Pytest fixtures for all tests.
Uses an in-memory SQLite database with sync SQLAlchemy.
"""
import os

# Point to SQLite BEFORE any app modules are imported so that
# pydantic-settings reads the test DATABASE_URL.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as app_db
from app.database import Base, get_db
from app.main import app
from app.models.user import Role, User
from app.services.auth_service import create_user

TEST_DB_URL = "sqlite://"  # in-memory

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Patch the module-level engine and SessionLocal so init_db() uses SQLite
app_db.engine = engine
app_db.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a DB session for a test, rolling back after."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Test client with the DB dependency overridden."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Role-specific user fixtures ────────────────────────────────────────────


def _make_user(db, role: str, email: str) -> User:
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).first()
    if not tenant:
        tenant = Tenant(name="Test Hospital", code="TST", is_active=True)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return create_user(db, email=email, password="Test@1234", full_name="Test User",
                       role=role, tenant_id=tenant.id)


@pytest.fixture
def doctor_user(db):
    return _make_user(db, Role.doctor, "doctor@test.com")


@pytest.fixture
def assistant_user(db):
    return _make_user(db, Role.assistant, "assistant@test.com")


@pytest.fixture
def admin_user(db):
    return _make_user(db, Role.hospital_admin, "admin@test.com")


@pytest.fixture
def pharmacist_user(db):
    return _make_user(db, Role.pharmacist, "pharmacist@test.com")


def _auth_headers(client, email: str, password: str = "Test@1234") -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def doctor_headers(client, doctor_user):
    return _auth_headers(client, "doctor@test.com")


@pytest.fixture
def assistant_headers(client, assistant_user):
    return _auth_headers(client, "assistant@test.com")


@pytest.fixture
def admin_headers(client, admin_user):
    return _auth_headers(client, "admin@test.com")
