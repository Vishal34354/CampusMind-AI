import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.material_chunk
import app.models.study_material
import app.models.user
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def normal_user(test_db):
    user = User(
        full_name="Normal Student",
        email="student@example.com",
        hashed_password=hash_password("Password123!"),
        role="user",
        is_admin=False,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db):
    user = User(
        full_name="Admin User",
        email="admin@example.com",
        hashed_password=hash_password("Password123!"),
        role="admin",
        is_admin=True,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def client():
    return TestClient(app)


def test_admin_users_unauthorized(client):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_admin_users_forbidden_for_normal_user(client, normal_user):
    token = create_access_token(subject=str(normal_user.id))
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


def test_admin_users_success_for_admin(client, admin_user, normal_user):
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert data["total"] == 2
    assert data["page"] == 1
    assert len(data["items"]) == 2

    first_user = data["items"][0]
    assert "hashed_password" not in first_user
    assert "password" not in first_user
    assert "role" in first_user
    assert "is_admin" in first_user
    assert "materials_count" in first_user


def test_admin_users_search_and_filter(client, admin_user, normal_user):
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/admin/users?search=student@example.com", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["email"] == "student@example.com"

    res = client.get("/api/v1/admin/users?status_filter=active", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 2


def test_admin_deactivate_user(client, admin_user, normal_user):
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    res = client.patch(
        f"/api/v1/admin/users/{normal_user.id}/status",
        headers=headers,
        json={"is_active": False},
    )
    assert res.status_code == 200
    assert res.json()["is_active"] is False


def test_admin_cannot_deactivate_self(client, admin_user):
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    res = client.patch(
        f"/api/v1/admin/users/{admin_user.id}/status",
        headers=headers,
        json={"is_active": False},
    )
    assert res.status_code == 400
    assert "cannot deactivate your own" in res.json()["detail"].lower()
