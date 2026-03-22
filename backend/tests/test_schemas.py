"""
Validation tests for Pydantic schemas.
Ensures request/response schemas enforce the correct types, required fields,
and validation rules (e.g., EmailStr format).
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas import (
    UserBase,
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
    CompanyBase,
    CompanyResponse,
    JobResponse,
    NewsResponse,
    SaveJobRequest,
    FollowCompanyRequest,
)


# ===========================================================================
# UserBase Schema Tests
# ===========================================================================
class TestUserBaseSchema:

    def test_valid_user_base(self):
        user = UserBase(name="Alice", email="alice@example.com")
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

    def test_missing_name(self):
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="alice@example.com")
        assert "name" in str(exc_info.value)

    def test_missing_email(self):
        with pytest.raises(ValidationError) as exc_info:
            UserBase(name="Alice")
        assert "email" in str(exc_info.value)

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError) as exc_info:
            UserBase(name="Alice", email="not-an-email")
        errors = exc_info.value.errors()
        assert any("email" in str(e).lower() for e in errors)

    def test_email_without_domain(self):
        with pytest.raises(ValidationError):
            UserBase(name="Alice", email="alice@")

    def test_email_without_at_sign(self):
        with pytest.raises(ValidationError):
            UserBase(name="Alice", email="aliceexample.com")

    def test_empty_name(self):
        """Empty string is technically valid for str type but may be undesirable."""
        user = UserBase(name="", email="alice@example.com")
        assert user.name == ""

    def test_name_with_special_characters(self):
        user = UserBase(name="O'Brien-Smith", email="obrien@example.com")
        assert user.name == "O'Brien-Smith"


# ===========================================================================
# UserCreate Schema Tests
# ===========================================================================
class TestUserCreateSchema:

    def test_valid_user_create(self):
        user = UserCreate(name="Bob", email="bob@example.com", password="SecurePass123!")
        assert user.password == "SecurePass123!"

    def test_missing_password(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="Bob", email="bob@example.com")
        assert "password" in str(exc_info.value)

    def test_inherits_email_validation(self):
        with pytest.raises(ValidationError):
            UserCreate(name="Bob", email="invalid", password="pass")

    def test_empty_password(self):
        """Empty password is valid at schema level (business logic may reject it)."""
        user = UserCreate(name="Bob", email="bob@example.com", password="")
        assert user.password == ""

    def test_very_long_password(self):
        long_pass = "A" * 500
        user = UserCreate(name="Bob", email="bob@example.com", password=long_pass)
        assert len(user.password) == 500


# ===========================================================================
# UserResponse Schema Tests
# ===========================================================================
class TestUserResponseSchema:

    def test_valid_user_response(self):
        user = UserResponse(id=1, name="Alice", email="alice@example.com", role="user")
        assert user.id == 1
        assert user.role == "user"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            UserResponse(name="Alice", email="alice@example.com", role="user")

    def test_missing_role(self):
        with pytest.raises(ValidationError):
            UserResponse(id=1, name="Alice", email="alice@example.com")

    def test_admin_role(self):
        user = UserResponse(id=2, name="Admin", email="admin@example.com", role="admin")
        assert user.role == "admin"

    def test_from_attributes_config(self):
        """Ensure from_attributes is enabled for ORM compatibility."""
        assert UserResponse.model_config.get("from_attributes") is True


# ===========================================================================
# Token Schema Tests
# ===========================================================================
class TestTokenSchema:

    def test_valid_token(self):
        user_resp = UserResponse(id=1, name="Alice", email="alice@example.com", role="user")
        token = Token(access_token="abc123", token_type="bearer", user=user_resp)
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"
        assert token.user.name == "Alice"

    def test_missing_access_token(self):
        user_resp = UserResponse(id=1, name="Alice", email="alice@example.com", role="user")
        with pytest.raises(ValidationError):
            Token(token_type="bearer", user=user_resp)

    def test_missing_user(self):
        with pytest.raises(ValidationError):
            Token(access_token="abc123", token_type="bearer")


# ===========================================================================
# LoginRequest Schema Tests
# ===========================================================================
class TestLoginRequestSchema:

    def test_valid_login(self):
        req = LoginRequest(email="user@example.com", password="pass123")
        assert req.email == "user@example.com"
        assert req.password == "pass123"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-valid", password="pass123")

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="pass123")


# ===========================================================================
# CompanyBase Schema Tests
# ===========================================================================
class TestCompanyBaseSchema:

    def test_valid_company_all_fields(self):
        company = CompanyBase(
            name="Google",
            industry="Technology",
            website="https://google.com",
            logo="G",
        )
        assert company.name == "Google"
        assert company.industry == "Technology"

    def test_company_optional_fields_default_none(self):
        company = CompanyBase(name="Startup")
        assert company.industry is None
        assert company.website is None
        assert company.logo is None

    def test_missing_company_name(self):
        with pytest.raises(ValidationError):
            CompanyBase()


# ===========================================================================
# CompanyResponse Schema Tests
# ===========================================================================
class TestCompanyResponseSchema:

    def test_valid_company_response(self):
        company = CompanyResponse(id=1, name="Meta", industry="Tech")
        assert company.id == 1
        assert company.name == "Meta"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            CompanyResponse(name="Meta")


# ===========================================================================
# JobResponse Schema Tests
# ===========================================================================
class TestJobResponseSchema:

    def test_valid_job_response_all_fields(self):
        job = JobResponse(
            id=1,
            title="SDE",
            company_id=1,
            location="SF",
            salary_min=100000.0,
            salary_max=150000.0,
            experience_level="Mid",
            description="Build stuff.",
            apply_url="https://apply.com",
            posted_date=datetime(2026, 1, 1),
            company=CompanyResponse(id=1, name="Corp"),
        )
        assert job.title == "SDE"
        assert job.company.name == "Corp"

    def test_job_response_optional_fields(self):
        job = JobResponse(
            id=2,
            title="Intern",
            company_id=1,
            location="Remote",
            description="Entry level.",
            posted_date=datetime(2026, 6, 1),
        )
        assert job.salary_min is None
        assert job.salary_max is None
        assert job.experience_level is None
        assert job.apply_url is None
        assert job.company is None

    def test_missing_required_title(self):
        with pytest.raises(ValidationError):
            JobResponse(
                id=1,
                company_id=1,
                location="SF",
                description="No title.",
                posted_date=datetime(2026, 1, 1),
            )

    def test_missing_required_description(self):
        with pytest.raises(ValidationError):
            JobResponse(
                id=1,
                title="SDE",
                company_id=1,
                location="SF",
                posted_date=datetime(2026, 1, 1),
            )

    def test_missing_required_posted_date(self):
        with pytest.raises(ValidationError):
            JobResponse(
                id=1,
                title="SDE",
                company_id=1,
                location="SF",
                description="Desc.",
            )

    def test_invalid_salary_type(self):
        with pytest.raises(ValidationError):
            JobResponse(
                id=1,
                title="SDE",
                company_id=1,
                location="SF",
                salary_min="not_a_number",
                description="Desc.",
                posted_date=datetime(2026, 1, 1),
            )


# ===========================================================================
# NewsResponse Schema Tests
# ===========================================================================
class TestNewsResponseSchema:

    def test_valid_news_response(self):
        news = NewsResponse(
            id=1,
            title="AI News",
            source="TechCrunch",
            category="Tech",
            summary="Big news.",
            url="https://example.com",
            published_date=datetime(2026, 3, 15),
        )
        assert news.title == "AI News"
        assert news.source == "TechCrunch"

    def test_news_optional_content(self):
        news = NewsResponse(
            id=1,
            title="Quick",
            source="BBC",
            category="World",
            summary="Headline.",
            url="https://bbc.com",
            published_date=datetime(2026, 1, 1),
        )
        assert news.content is None

    def test_missing_required_source(self):
        with pytest.raises(ValidationError):
            NewsResponse(
                id=1,
                title="No Source",
                category="Tech",
                summary="Test.",
                url="https://example.com",
                published_date=datetime(2026, 1, 1),
            )

    def test_missing_required_url(self):
        with pytest.raises(ValidationError):
            NewsResponse(
                id=1,
                title="No URL",
                source="Test",
                category="Tech",
                summary="Test.",
                published_date=datetime(2026, 1, 1),
            )

    def test_invalid_published_date_type(self):
        with pytest.raises(ValidationError):
            NewsResponse(
                id=1,
                title="Bad Date",
                source="Test",
                category="Tech",
                summary="Test.",
                url="https://example.com",
                published_date="not-a-date",
            )


# ===========================================================================
# SaveJobRequest Schema Tests
# ===========================================================================
class TestSaveJobRequestSchema:

    def test_valid_request(self):
        req = SaveJobRequest(job_id=42)
        assert req.job_id == 42

    def test_missing_job_id(self):
        with pytest.raises(ValidationError):
            SaveJobRequest()

    def test_invalid_job_id_type(self):
        with pytest.raises(ValidationError):
            SaveJobRequest(job_id="abc")


# ===========================================================================
# FollowCompanyRequest Schema Tests
# ===========================================================================
class TestFollowCompanyRequestSchema:

    def test_valid_request(self):
        req = FollowCompanyRequest(company_id=7)
        assert req.company_id == 7

    def test_missing_company_id(self):
        with pytest.raises(ValidationError):
            FollowCompanyRequest()

    def test_invalid_company_id_type(self):
        with pytest.raises(ValidationError):
            FollowCompanyRequest(company_id="xyz")
