"""
Integration tests for the Jobs API endpoints (/api/jobs/*).
Tests listing, filtering, pagination, single job retrieval, and company jobs.
"""
import pytest
from app.models import Job, Company


class TestGetJobs:

    def test_get_jobs_empty(self, client):
        """Test jobs endpoint returns empty list when no jobs exist."""
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_get_jobs_with_data(self, client, sample_job):
        """Test jobs endpoint returns existing jobs."""
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_get_jobs_pagination(self, client, db, sample_company):
        """Test pagination returns correct number of items."""
        for i in range(15):
            db.add(Job(
                title=f"Job {i}",
                company_id=sample_company.id,
                location="Remote",
                description=f"Description {i}",
            ))
        db.commit()

        # Page 1 with limit 5
        response = client.get("/api/jobs/?page=1&limit=5")
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 15
        assert data["pages"] == 3

        # Page 2 with limit 5
        response = client.get("/api/jobs/?page=2&limit=5")
        data = response.json()
        assert len(data["items"]) == 5

    def test_get_jobs_search_by_title(self, client, db, sample_company):
        """Test filtering jobs by search query matching title."""
        db.add(Job(title="Python Developer", company_id=sample_company.id, location="NYC", description="Python work."))
        db.add(Job(title="Java Developer", company_id=sample_company.id, location="LA", description="Java work."))
        db.commit()

        response = client.get("/api/jobs/?q=Python")
        data = response.json()
        assert data["total"] >= 1
        assert all("Python" in item["title"] for item in data["items"])

    def test_get_jobs_search_by_description(self, client, db, sample_company):
        """Test filtering jobs by search query matching description."""
        db.add(Job(title="SDE", company_id=sample_company.id, location="SF", description="Work with Kubernetes clusters."))
        db.commit()

        response = client.get("/api/jobs/?q=Kubernetes")
        data = response.json()
        assert data["total"] >= 1

    def test_get_jobs_filter_by_location(self, client, db, sample_company):
        """Test filtering jobs by location."""
        db.add(Job(title="Job A", company_id=sample_company.id, location="San Francisco", description="A"))
        db.add(Job(title="Job B", company_id=sample_company.id, location="New York", description="B"))
        db.commit()

        response = client.get("/api/jobs/?location=San Francisco")
        data = response.json()
        assert all("San Francisco" in item["location"] for item in data["items"])

    def test_get_jobs_filter_by_experience(self, client, db, sample_company):
        """Test filtering jobs by experience level."""
        db.add(Job(title="Senior Dev", company_id=sample_company.id, location="Remote", experience_level="Senior", description="Lead."))
        db.add(Job(title="Junior Dev", company_id=sample_company.id, location="Remote", experience_level="Junior", description="Learn."))
        db.commit()

        response = client.get("/api/jobs/?experience=Senior")
        data = response.json()
        assert all("Senior" in (item.get("experience_level") or "") for item in data["items"])

    def test_get_jobs_filter_by_company(self, client, db):
        """Test filtering jobs by company name."""
        company = Company(name="FilterCorp", industry="AI")
        db.add(company)
        db.commit()
        db.refresh(company)

        db.add(Job(title="AI Eng", company_id=company.id, location="Remote", description="AI."))
        db.commit()

        response = client.get("/api/jobs/?company=FilterCorp")
        data = response.json()
        assert data["total"] >= 1

    def test_get_jobs_pages_calculation(self, client, db, sample_company):
        """Test that pages count is calculated correctly."""
        for i in range(7):
            db.add(Job(title=f"Job {i}", company_id=sample_company.id, location="X", description="D"))
        db.commit()

        response = client.get("/api/jobs/?limit=3")
        data = response.json()
        assert data["pages"] == 3  # ceil(7/3) = 3

    def test_get_jobs_response_includes_company(self, client, sample_job):
        """Test that job items include nested company data."""
        response = client.get("/api/jobs/")
        data = response.json()
        for item in data["items"]:
            if item["id"] == sample_job.id:
                assert item["company"] is not None
                assert "name" in item["company"]


class TestGetSingleJob:

    def test_get_job_by_id(self, client, sample_job):
        """Test retrieving a single job by its ID."""
        response = client.get(f"/api/jobs/{sample_job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_job.id
        assert data["title"] == sample_job.title

    def test_get_job_includes_company(self, client, sample_job, sample_company):
        """Test that single job response includes company info."""
        response = client.get(f"/api/jobs/{sample_job.id}")
        data = response.json()
        assert data["company"]["name"] == sample_company.name

    def test_get_nonexistent_job(self, client):
        """Test retrieving a job with an ID that doesn't exist."""
        response = client.get("/api/jobs/99999")
        assert response.status_code == 404


class TestGetCompanyJobs:

    def test_get_jobs_by_company(self, client, db, sample_company):
        """Test listing jobs for a specific company."""
        db.add(Job(title="Job X", company_id=sample_company.id, location="A", description="X"))
        db.add(Job(title="Job Y", company_id=sample_company.id, location="B", description="Y"))
        db.commit()

        response = client.get(f"/api/jobs/company/{sample_company.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_jobs_by_nonexistent_company(self, client):
        """Test listing jobs for a company that doesn't exist returns empty."""
        response = client.get("/api/jobs/company/99999")
        assert response.status_code == 200
        assert response.json() == []
