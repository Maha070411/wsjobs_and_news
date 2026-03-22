"""
Integration tests for the News API endpoints (/api/news/*).
Tests listing, pagination, and single news article retrieval.
"""
import pytest
from app.models import News


class TestGetNews:

    def test_get_news_empty(self, client):
        """Test news endpoint returns empty list when no articles exist."""
        response = client.get("/api/news/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_news_with_data(self, client, sample_news):
        """Test news endpoint returns existing articles."""
        response = client.get("/api/news/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_get_news_pagination(self, client, db):
        """Test news pagination."""
        for i in range(12):
            db.add(News(
                title=f"Article {i}",
                source="TestSource",
                category="Tech",
                summary=f"Summary {i}",
                url=f"https://example.com/article-{i}",
            ))
        db.commit()

        # Page 1 with limit 5
        response = client.get("/api/news/?page=1&limit=5")
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 12
        assert data["pages"] == 3  # ceil(12/5) = 3

    def test_get_news_page_2(self, client, db):
        """Test fetching the second page of news articles."""
        for i in range(8):
            db.add(News(
                title=f"Article {i}",
                source="Source",
                category="Cat",
                summary=f"Sum {i}",
                url=f"https://example.com/{i}",
            ))
        db.commit()

        response = client.get("/api/news/?page=2&limit=5")
        data = response.json()
        assert len(data["items"]) == 3  # 8 - 5 = 3

    def test_get_news_ordered_by_date_desc(self, client, db):
        """Test that news is ordered by published_date descending."""
        from datetime import datetime, UTC
        old = News(title="Old", source="S", category="C", summary="X", url="https://a.com")
        old.published_date = datetime(2025, 1, 1, tzinfo=UTC)
        new = News(title="New", source="S", category="C", summary="X", url="https://b.com")
        new.published_date = datetime(2026, 6, 1, tzinfo=UTC)
        db.add_all([old, new])
        db.commit()

        response = client.get("/api/news/")
        data = response.json()
        # The newer article should come first
        assert data["items"][0]["title"] == "New"

    def test_get_news_response_fields(self, client, sample_news):
        """Test that news response contains all expected fields."""
        response = client.get("/api/news/")
        data = response.json()
        item = data["items"][0]
        expected_fields = ["id", "title", "source", "category", "summary", "url", "published_date"]
        for field in expected_fields:
            assert field in item, f"Missing field: {field}"

    def test_get_news_pages_calculation_exact_division(self, client, db):
        """Test pages calculation when total divides evenly by limit."""
        for i in range(10):
            db.add(News(
                title=f"Art {i}", source="S", category="C", summary="X",
                url=f"https://x.com/{i}",
            ))
        db.commit()

        response = client.get("/api/news/?limit=5")
        data = response.json()
        assert data["pages"] == 2


class TestGetNewsDetail:

    def test_get_news_by_id(self, client, sample_news):
        """Test retrieving a single news article by ID."""
        response = client.get(f"/api/news/{sample_news.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_news.id
        assert data["title"] == sample_news.title
        assert data["source"] == sample_news.source

    def test_get_nonexistent_news(self, client):
        """Test retrieving a news article that doesn't exist."""
        response = client.get("/api/news/99999")
        assert response.status_code == 404

    def test_news_detail_includes_content(self, client, sample_news):
        """Test that news detail includes content field."""
        response = client.get(f"/api/news/{sample_news.id}")
        data = response.json()
        assert "content" in data
