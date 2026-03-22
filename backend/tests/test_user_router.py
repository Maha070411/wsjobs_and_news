"""
Integration tests for User API endpoints (/api/user/*).
Tests dashboard, save-job, and follow-company with auth.
"""
import pytest
from app.models import Job, Company, SavedJob, FollowedCompany


class TestUserDashboard:

    def test_dashboard_unauthenticated(self, client):
        """Test dashboard returns 401 without authentication."""
        response = client.get("/api/user/dashboard")
        assert response.status_code == 401

    def test_dashboard_empty(self, client, auth_headers):
        """Test dashboard returns empty lists for a fresh user."""
        response = client.get("/api/user/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["saved_jobs"] == []
        assert data["followed_companies"] == []

    def test_dashboard_with_saved_jobs(self, client, db, sample_user, sample_job, auth_headers):
        """Test dashboard shows saved jobs."""
        db.add(SavedJob(user_id=sample_user.id, job_id=sample_job.id))
        db.commit()

        response = client.get("/api/user/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["saved_jobs"]) == 1

    def test_dashboard_with_followed_companies(self, client, db, sample_user, sample_company, auth_headers):
        """Test dashboard shows followed companies."""
        db.add(FollowedCompany(user_id=sample_user.id, company_id=sample_company.id))
        db.commit()

        response = client.get("/api/user/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["followed_companies"]) == 1


class TestSaveJob:

    def test_save_job_unauthenticated(self, client):
        """Test saving a job without auth returns 401."""
        response = client.post("/api/user/save-job", json={"job_id": 1})
        assert response.status_code == 401

    def test_save_job_success(self, client, sample_job, auth_headers):
        """Test saving a job successfully."""
        response = client.post("/api/user/save-job", json={"job_id": sample_job.id}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_save_job_duplicate(self, client, sample_job, auth_headers):
        """Test saving the same job twice still returns success (idempotent)."""
        client.post("/api/user/save-job", json={"job_id": sample_job.id}, headers=auth_headers)
        response = client.post("/api/user/save-job", json={"job_id": sample_job.id}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_save_job_duplicate_does_not_create_duplicate(self, client, db, sample_user, sample_job, auth_headers):
        """Test saving the same job twice does NOT create a duplicate record."""
        client.post("/api/user/save-job", json={"job_id": sample_job.id}, headers=auth_headers)
        client.post("/api/user/save-job", json={"job_id": sample_job.id}, headers=auth_headers)

        count = db.query(SavedJob).filter_by(user_id=sample_user.id, job_id=sample_job.id).count()
        assert count == 1

    def test_save_job_missing_job_id(self, client, auth_headers):
        """Test save-job without job_id returns 422."""
        response = client.post("/api/user/save-job", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_save_job_invalid_job_id_type(self, client, auth_headers):
        """Test save-job with invalid job_id type returns 422."""
        response = client.post("/api/user/save-job", json={"job_id": "abc"}, headers=auth_headers)
        assert response.status_code == 422


class TestFollowCompany:

    def test_follow_company_unauthenticated(self, client):
        """Test following a company without auth returns 401."""
        response = client.post("/api/user/follow-company", json={"company_id": 1})
        assert response.status_code == 401

    def test_follow_company_success(self, client, sample_company, auth_headers):
        """Test following a company successfully."""
        response = client.post("/api/user/follow-company", json={"company_id": sample_company.id}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_follow_company_duplicate(self, client, sample_company, auth_headers):
        """Test following the same company twice returns success (idempotent)."""
        client.post("/api/user/follow-company", json={"company_id": sample_company.id}, headers=auth_headers)
        response = client.post("/api/user/follow-company", json={"company_id": sample_company.id}, headers=auth_headers)
        assert response.status_code == 200

    def test_follow_company_duplicate_does_not_create_duplicate(self, client, db, sample_user, sample_company, auth_headers):
        """Test following the same company twice does NOT create a duplicate."""
        client.post("/api/user/follow-company", json={"company_id": sample_company.id}, headers=auth_headers)
        client.post("/api/user/follow-company", json={"company_id": sample_company.id}, headers=auth_headers)

        count = db.query(FollowedCompany).filter_by(user_id=sample_user.id, company_id=sample_company.id).count()
        assert count == 1

    def test_follow_company_missing_company_id(self, client, auth_headers):
        """Test follow-company without company_id returns 422."""
        response = client.post("/api/user/follow-company", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_follow_company_invalid_company_id_type(self, client, auth_headers):
        """Test follow-company with invalid company_id type returns 422."""
        response = client.post("/api/user/follow-company", json={"company_id": "xyz"}, headers=auth_headers)
        assert response.status_code == 422
