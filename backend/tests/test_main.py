"""
Integration tests for root-level endpoints defined in main.py.
Tests the root, summary stats, and top companies endpoints.
"""
import pytest
from app.models import Job, Company, News


class TestRootEndpoint:

    def test_read_root(self, client):
        """Test the root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to JobHub API"}

    def test_root_is_get_only(self, client):
        """Test that POST to root is not allowed."""
        response = client.post("/")
        assert response.status_code == 405


class TestAppSummary:

    def test_summary_empty_database(self, client):
        """Test summary with no data returns zeros."""
        response = client.get("/api/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["jobs"] == 0
        assert data["companies"] == 0
        assert data["news"] == 0

    def test_summary_with_data(self, client, sample_job, sample_news):
        """Test summary returns correct counts."""
        response = client.get("/api/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["jobs"] >= 1
        assert data["companies"] >= 1
        assert data["news"] >= 1

    def test_summary_response_fields(self, client):
        """Test that summary response contains all expected keys."""
        response = client.get("/api/stats/summary")
        data = response.json()
        assert "jobs" in data
        assert "companies" in data
        assert "news" in data

    def test_summary_values_are_integers(self, client):
        """Test that summary values are integers."""
        response = client.get("/api/stats/summary")
        data = response.json()
        for key in ["jobs", "companies", "news"]:
            assert isinstance(data[key], int)


class TestTopCompanies:

    def test_top_companies_empty(self, client):
        """Test top companies returns empty list when none exist."""
        response = client.get("/api/companies/top")
        assert response.status_code == 200
        assert response.json() == []

    def test_top_companies_with_data(self, client, sample_company):
        """Test top companies returns companies when data exists."""
        response = client.get("/api/companies/top")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_top_companies_response_fields(self, client, sample_company):
        """Test that each company in top companies has expected fields."""
        response = client.get("/api/companies/top")
        data = response.json()
        for company in data:
            assert "name" in company
            assert "id" in company
            assert "industry" in company

    def test_top_companies_multiple(self, client, db):
        """Test top companies returns all companies."""
        for i in range(5):
            db.add(Company(name=f"Company{i}", industry=f"Industry{i}"))
        db.commit()

        response = client.get("/api/companies/top")
        data = response.json()
        assert len(data) == 5
