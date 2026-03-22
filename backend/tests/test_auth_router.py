"""
Integration tests for authentication API endpoints (/api/auth/*).
Tests registration, login, duplicate email, invalid credentials, and /me endpoint.
"""
import pytest


class TestRegisterEndpoint:

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "StrongPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data  # Password should NOT be in response

    def test_register_first_user_is_admin(self, client):
        """Test that the first user registered gets the admin role."""
        response = client.post("/api/auth/register", json={
            "name": "First User",
            "email": "first@example.com",
            "password": "Pass123!"
        })
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_register_second_user_is_regular(self, client):
        """Test that subsequent users get the 'user' role."""
        # First user (admin)
        client.post("/api/auth/register", json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "Pass123!"
        })
        # Second user (regular)
        response = client.post("/api/auth/register", json={
            "name": "Regular",
            "email": "regular@example.com",
            "password": "Pass123!"
        })
        assert response.status_code == 200
        assert response.json()["role"] == "user"

    def test_register_duplicate_email(self, client):
        """Test that registering with an already used email returns 400."""
        client.post("/api/auth/register", json={
            "name": "User1",
            "email": "duplicate@example.com",
            "password": "Pass123!"
        })
        response = client.post("/api/auth/register", json={
            "name": "User2",
            "email": "duplicate@example.com",
            "password": "Pass456!"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email_format(self, client):
        """Test registration with an invalid email format."""
        response = client.post("/api/auth/register", json={
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "Pass123!"
        })
        assert response.status_code == 422  # Validation error

    def test_register_missing_name(self, client):
        """Test registration without a name field."""
        response = client.post("/api/auth/register", json={
            "email": "noname@example.com",
            "password": "Pass123!"
        })
        assert response.status_code == 422

    def test_register_missing_password(self, client):
        """Test registration without a password."""
        response = client.post("/api/auth/register", json={
            "name": "No Pass",
            "email": "nopass@example.com"
        })
        assert response.status_code == 422

    def test_register_missing_email(self, client):
        """Test registration without an email."""
        response = client.post("/api/auth/register", json={
            "name": "No Email",
            "password": "Pass123!"
        })
        assert response.status_code == 422

    def test_register_empty_body(self, client):
        """Test registration with an empty payload."""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422


class TestLoginEndpoint:

    def _create_user(self, client, email="login@example.com", password="Login123!"):
        """Helper to register a test user."""
        client.post("/api/auth/register", json={
            "name": "Login User",
            "email": email,
            "password": password
        })

    def test_login_success(self, client):
        """Test successful login returns access token and user info."""
        self._create_user(client)
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "Login123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client):
        """Test login with incorrect password returns 401."""
        self._create_user(client)
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "WrongPassword!"
        })
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with unregistered email returns 401."""
        response = client.post("/api/auth/login", json={
            "email": "noexist@example.com",
            "password": "Pass123!"
        })
        assert response.status_code == 401

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post("/api/auth/login", json={
            "email": "bad-email",
            "password": "Pass123!"
        })
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Test login without password field."""
        response = client.post("/api/auth/login", json={
            "email": "login@example.com"
        })
        assert response.status_code == 422

    def test_login_empty_body(self, client):
        """Test login with empty payload."""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422


class TestMeEndpoint:

    def test_get_me_authenticated(self, client, sample_user, auth_headers):
        """Test /me returns current user info when authenticated."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user.email
        assert data["name"] == sample_user.name

    def test_get_me_unauthenticated(self, client):
        """Test /me returns 401 without a token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Test /me returns 401 with an invalid token."""
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid-token-here"
        })
        assert response.status_code == 401
