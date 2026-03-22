"""
Unit tests for SQLAlchemy entity models.
Validates field constraints, defaults, relationships, and data integrity.
"""
import pytest
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError

from app.models import User, Company, Job, News, SavedJob, FollowedCompany


# ===========================================================================
# User Model Tests
# ===========================================================================
class TestUserModel:

    def test_create_user_with_valid_data(self, db):
        """Test creating a user with all valid fields."""
        user = User(
            name="John Doe",
            email="john@example.com",
            password_hash="hashed_password",
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.password_hash == "hashed_password"
        assert user.role == "user"

    def test_user_default_role(self, db):
        """Test that the default role is 'user'."""
        user = User(name="Jane", email="jane@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.role == "user"

    def test_user_created_at_default(self, db):
        """Test that created_at is auto-populated."""
        user = User(name="Test", email="test@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_email_uniqueness(self, db):
        """Test that duplicate emails raise IntegrityError."""
        user1 = User(name="User1", email="dup@example.com", password_hash="hash1")
        db.add(user1)
        db.commit()

        user2 = User(name="User2", email="dup@example.com", password_hash="hash2")
        db.add(user2)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_user_admin_role(self, db):
        """Test that a user can be created with admin role."""
        admin = User(name="Admin", email="admin@test.com", password_hash="hash", role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)

        assert admin.role == "admin"

    def test_user_name_max_length(self, db):
        """Test that the name field stores up to 100 characters."""
        long_name = "A" * 100
        user = User(name=long_name, email="longname@test.com", password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.name == long_name

    def test_user_email_max_length(self, db):
        """Test that 100-char email is accepted by the model."""
        # Build a valid-looking email near the 100 char mark
        email = "a" * 88 + "@test.co.in"  # 100 chars
        user = User(name="Test", email=email, password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.email == email

    def test_user_id_auto_increment(self, db):
        """Test that user IDs auto-increment."""
        u1 = User(name="A", email="a@test.com", password_hash="h")
        u2 = User(name="B", email="b@test.com", password_hash="h")
        db.add_all([u1, u2])
        db.commit()
        db.refresh(u1)
        db.refresh(u2)

        assert u2.id == u1.id + 1


# ===========================================================================
# Company Model Tests
# ===========================================================================
class TestCompanyModel:

    def test_create_company_with_all_fields(self, db):
        """Test creating a company with all details."""
        company = Company(
            name="Google",
            industry="Technology",
            website="https://google.com",
            logo="G",
        )
        db.add(company)
        db.commit()
        db.refresh(company)

        assert company.id is not None
        assert company.name == "Google"
        assert company.industry == "Technology"
        assert company.website == "https://google.com"
        assert company.logo == "G"

    def test_create_company_with_only_required_fields(self, db):
        """Test creating a company with only the name (other fields nullable)."""
        company = Company(name="StartupX")
        db.add(company)
        db.commit()
        db.refresh(company)

        assert company.id is not None
        assert company.name == "StartupX"
        assert company.industry is None
        assert company.website is None
        assert company.logo is None

    def test_company_name_max_length(self, db):
        """Test that a 100-character company name is stored correctly."""
        name = "C" * 100
        company = Company(name=name)
        db.add(company)
        db.commit()
        db.refresh(company)

        assert company.name == name

    def test_multiple_companies(self, db):
        """Test creating multiple companies."""
        companies = [
            Company(name="CompanyA", industry="Tech"),
            Company(name="CompanyB", industry="Finance"),
            Company(name="CompanyC", industry="Healthcare"),
        ]
        db.add_all(companies)
        db.commit()

        all_companies = db.query(Company).all()
        assert len(all_companies) == 3


# ===========================================================================
# Job Model Tests
# ===========================================================================
class TestJobModel:

    def test_create_job_with_all_fields(self, db, sample_company):
        """Test creating a job with all fields populated."""
        job = Job(
            title="Backend Developer",
            company_id=sample_company.id,
            location="New York",
            salary_min=100000.0,
            salary_max=150000.0,
            experience_level="Senior",
            description="Build REST APIs.",
            apply_url="https://apply.com/job1",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        assert job.id is not None
        assert job.title == "Backend Developer"
        assert job.company_id == sample_company.id
        assert job.salary_min == 100000.0
        assert job.salary_max == 150000.0
        assert job.experience_level == "Senior"

    def test_job_nullable_fields(self, db, sample_company):
        """Test that salary, experience, and apply_url can be None."""
        job = Job(
            title="Intern",
            company_id=sample_company.id,
            location="Remote",
            description="Entry level position.",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        assert job.salary_min is None
        assert job.salary_max is None
        assert job.experience_level is None
        assert job.apply_url is None

    def test_job_posted_date_default(self, db, sample_company):
        """Test that posted_date is automatically set."""
        job = Job(
            title="DevOps",
            company_id=sample_company.id,
            location="Austin",
            description="CI/CD pipelines.",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        assert job.posted_date is not None
        assert isinstance(job.posted_date, datetime)

    def test_job_created_at_default(self, db, sample_company):
        """Test that created_at is automatically set."""
        job = Job(
            title="QA",
            company_id=sample_company.id,
            location="London",
            description="Testing.",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        assert job.created_at is not None

    def test_job_company_relationship(self, db, sample_company):
        """Test that the Job -> Company relationship is loaded."""
        job = Job(
            title="Data Scientist",
            company_id=sample_company.id,
            location="Berlin",
            description="ML models.",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        assert job.company is not None
        assert job.company.name == sample_company.name

    def test_job_salary_range_values(self, db, sample_company):
        """Test storing various salary float values."""
        job = Job(
            title="Lead",
            company_id=sample_company.id,
            location="Remote",
            salary_min=50000.50,
            salary_max=99999.99,
            description="Lead role.",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        assert job.salary_min == pytest.approx(50000.50)
        assert job.salary_max == pytest.approx(99999.99)


# ===========================================================================
# News Model Tests
# ===========================================================================
class TestNewsModel:

    def test_create_news_with_all_fields(self, db):
        """Test creating a news article with all fields."""
        news = News(
            title="Breaking News",
            source="Reuters",
            category="World",
            summary="Something happened.",
            content="Full details here.",
            url="https://reuters.com/article",
        )
        db.add(news)
        db.commit()
        db.refresh(news)

        assert news.id is not None
        assert news.title == "Breaking News"
        assert news.source == "Reuters"
        assert news.category == "World"

    def test_news_content_nullable(self, db):
        """Test that news content can be None."""
        news = News(
            title="Quick Update",
            source="BBC",
            category="Tech",
            summary="A brief update.",
            url="https://bbc.com/tech",
        )
        db.add(news)
        db.commit()
        db.refresh(news)

        assert news.content is None

    def test_news_published_date_default(self, db):
        """Test that published_date is automatically set."""
        news = News(
            title="Auto Date",
            source="CNN",
            category="Science",
            summary="Testing default date.",
            url="https://cnn.com",
        )
        db.add(news)
        db.commit()
        db.refresh(news)

        assert news.published_date is not None
        assert isinstance(news.published_date, datetime)

    def test_news_url_stores_long_urls(self, db):
        """Test that a long URL (up to 500 chars) is stored."""
        long_url = "https://example.com/" + "a" * 475
        news = News(
            title="Long URL",
            source="Test",
            category="Other",
            summary="Testing long URL.",
            url=long_url,
        )
        db.add(news)
        db.commit()
        db.refresh(news)

        assert news.url == long_url


# ===========================================================================
# SavedJob Model Tests
# ===========================================================================
class TestSavedJobModel:

    def test_create_saved_job(self, db, sample_user, sample_job):
        """Test saving a job for a user."""
        saved = SavedJob(user_id=sample_user.id, job_id=sample_job.id)
        db.add(saved)
        db.commit()
        db.refresh(saved)

        assert saved.id is not None
        assert saved.user_id == sample_user.id
        assert saved.job_id == sample_job.id

    def test_multiple_saved_jobs_for_user(self, db, sample_user, sample_company):
        """Test that a user can save multiple jobs."""
        jobs = []
        for i in range(3):
            job = Job(
                title=f"Job {i}",
                company_id=sample_company.id,
                location="Remote",
                description=f"Description {i}",
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            jobs.append(job)

        for job in jobs:
            db.add(SavedJob(user_id=sample_user.id, job_id=job.id))
        db.commit()

        saved_count = db.query(SavedJob).filter(SavedJob.user_id == sample_user.id).count()
        assert saved_count == 3


# ===========================================================================
# FollowedCompany Model Tests
# ===========================================================================
class TestFollowedCompanyModel:

    def test_follow_company(self, db, sample_user, sample_company):
        """Test following a company."""
        follow = FollowedCompany(user_id=sample_user.id, company_id=sample_company.id)
        db.add(follow)
        db.commit()
        db.refresh(follow)

        assert follow.id is not None
        assert follow.user_id == sample_user.id
        assert follow.company_id == sample_company.id

    def test_user_can_follow_multiple_companies(self, db, sample_user):
        """Test that a user can follow multiple companies."""
        for i in range(3):
            company = Company(name=f"Corp{i}")
            db.add(company)
            db.commit()
            db.refresh(company)
            db.add(FollowedCompany(user_id=sample_user.id, company_id=company.id))
        db.commit()

        count = db.query(FollowedCompany).filter(FollowedCompany.user_id == sample_user.id).count()
        assert count == 3
