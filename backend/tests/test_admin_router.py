"""
Integration tests for Admin API endpoints (/api/admin/*).
Tests stats, scrapers listing, scraper triggering, toggling, and auth guards.
"""
import pytest


class TestAdminStats:

    def test_stats_as_admin(self, client, admin_headers):
        """Test stats endpoint returns counts for admin user."""
        response = client.get("/api/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "users" in data
        assert "companies" in data
        assert "news" in data

    def test_stats_unauthenticated(self, client):
        """Test stats returns 401 without auth."""
        response = client.get("/api/admin/stats")
        assert response.status_code == 401

    def test_stats_as_regular_user(self, client, auth_headers):
        """Test stats returns 403 for non-admin users."""
        response = client.get("/api/admin/stats", headers=auth_headers)
        assert response.status_code == 403

    def test_stats_returns_integers(self, client, admin_headers):
        """Test that all stat values are integers."""
        response = client.get("/api/admin/stats", headers=admin_headers)
        data = response.json()
        for key in ["jobs", "users", "companies", "news"]:
            assert isinstance(data[key], int)


class TestAdminScrapers:

    def test_get_scrapers_as_admin(self, client, admin_headers):
        """Test scrapers list is returned for admin."""
        response = client.get("/api/admin/scrapers", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_scrapers_have_required_fields(self, client, admin_headers):
        """Test each scraper has expected fields."""
        response = client.get("/api/admin/scrapers", headers=admin_headers)
        data = response.json()
        for scraper in data:
            assert "id" in scraper
            assert "name" in scraper
            assert "status" in scraper
            assert "interval" in scraper
            assert "lastRun" in scraper
            assert "running" in scraper

    def test_get_scrapers_unauthenticated(self, client):
        """Test scrapers returns 401 without auth."""
        response = client.get("/api/admin/scrapers")
        assert response.status_code == 401

    def test_get_scrapers_as_regular_user(self, client, auth_headers):
        """Test scrapers returns 403 for non-admin users."""
        response = client.get("/api/admin/scrapers", headers=auth_headers)
        assert response.status_code == 403


class TestTriggerScraper:

    def test_trigger_scraper_as_admin(self, client, admin_headers):
        """Test triggering a scraper returns success."""
        response = client.post("/api/admin/scraper/run?scraper_id=jobs_scraper", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "triggered"
        assert data["scraper_id"] == "jobs_scraper"

    def test_trigger_scraper_unauthenticated(self, client):
        """Test triggering a scraper without auth returns 401."""
        response = client.post("/api/admin/scraper/run?scraper_id=jobs_scraper")
        assert response.status_code == 401

    def test_trigger_scraper_as_regular_user(self, client, auth_headers):
        """Test triggering a scraper as non-admin returns 403."""
        response = client.post("/api/admin/scraper/run?scraper_id=jobs_scraper", headers=auth_headers)
        assert response.status_code == 403


class TestToggleScraper:

    def test_toggle_scraper_as_admin(self, client, admin_headers):
        """Test toggling a scraper returns success."""
        response = client.post("/api/admin/scraper/toggle?scraper_id=news_scraper", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "toggled"
        assert data["scraper_id"] == "news_scraper"

    def test_toggle_scraper_unauthenticated(self, client):
        """Test toggling a scraper without auth returns 401."""
        response = client.post("/api/admin/scraper/toggle?scraper_id=news_scraper")
        assert response.status_code == 401

    def test_toggle_scraper_as_regular_user(self, client, auth_headers):
        """Test toggling a scraper as non-admin returns 403."""
        response = client.post("/api/admin/scraper/toggle?scraper_id=news_scraper", headers=auth_headers)
        assert response.status_code == 403
