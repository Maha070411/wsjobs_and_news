"""
Shared test fixtures for all backend tests.
Uses an in-memory SQLite database so tests never touch production data.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, Company, Job, News, SavedJob, FollowedCompany
from app.auth import get_password_hash, create_access_token


# ---------------------------------------------------------------------------
# In-memory SQLite engine for testing
# ---------------------------------------------------------------------------
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a transactional database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """FastAPI TestClient wired to the test database."""
    return TestClient(app)


@pytest.fixture
def sample_user(db):
    """Create and return a regular user."""
    user = User(
        name="Test User",
        email="testuser@example.com",
        password_hash=get_password_hash("Password123!"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_admin(db):
    """Create and return an admin user."""
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(sample_user):
    """Return a valid JWT for the regular user."""
    return create_access_token(data={"sub": str(sample_user.id), "role": sample_user.role})


@pytest.fixture
def admin_token(sample_admin):
    """Return a valid JWT for the admin user."""
    return create_access_token(data={"sub": str(sample_admin.id), "role": sample_admin.role})


@pytest.fixture
def auth_headers(user_token):
    """Authorization headers for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_company(db):
    """Create and return a sample company."""
    company = Company(
        name="TechCorp",
        industry="Technology",
        website="https://techcorp.com",
        logo="T",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def sample_job(db, sample_company):
    """Create and return a sample job."""
    job = Job(
        title="Software Engineer",
        company_id=sample_company.id,
        location="San Francisco, CA",
        salary_min=120000.0,
        salary_max=180000.0,
        experience_level="Mid",
        description="Build scalable web applications using modern technologies.",
        apply_url="https://techcorp.com/apply",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def sample_news(db):
    """Create and return a sample news article."""
    article = News(
        title="AI Trends 2026",
        source="TechCrunch",
        category="Trends",
        summary="The latest trends in artificial intelligence.",
        content="Full content of the article goes here.",
        url="https://techcrunch.com/ai-trends",
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
