"""
Unit tests for authentication utilities.
Covers password hashing/verification, JWT creation/decoding, and user retrieval.
"""
import pytest
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from fastapi import HTTPException

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.config import settings


# ===========================================================================
# Password Hashing & Verification Tests
# ===========================================================================
class TestPasswordHashing:

    def test_hash_password(self):
        """Test that a password can be hashed."""
        hashed = get_password_hash("MySecurePassword123!")
        assert hashed is not None
        assert hashed != "MySecurePassword123!"
        assert isinstance(hashed, str)

    def test_hash_produces_different_results(self):
        """Test that hashing the same password twice produces different hashes (due to salting)."""
        hash1 = get_password_hash("SamePassword")
        hash2 = get_password_hash("SamePassword")
        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Test that a correct password is verified successfully."""
        password = "CorrectPassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Test that an incorrect password fails verification."""
        hashed = get_password_hash("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_empty_password(self):
        """Test verification with an empty password."""
        hashed = get_password_hash("SomePassword")
        assert verify_password("", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing an empty password (should still produce a valid hash)."""
        hashed = get_password_hash("")
        assert hashed is not None
        assert verify_password("", hashed) is True

    def test_hash_special_characters(self):
        """Test hashing a password with special characters."""
        special_pwd = "P@$$w0rd!#%^&*()"
        hashed = get_password_hash(special_pwd)
        assert verify_password(special_pwd, hashed) is True

    def test_hash_unicode_password(self):
        """Test hashing a password with unicode characters."""
        unicode_pwd = "密码テスト123"
        hashed = get_password_hash(unicode_pwd)
        assert verify_password(unicode_pwd, hashed) is True

    def test_hash_very_long_password(self):
        """Test that bcrypt raises ValueError for passwords exceeding 72 bytes."""
        long_pwd = "A" * 100
        with pytest.raises(ValueError):
            get_password_hash(long_pwd)


# ===========================================================================
# JWT Token Tests
# ===========================================================================
class TestJWTTokens:

    def test_create_access_token(self):
        """Test that an access token is created successfully."""
        token = create_access_token(data={"sub": "1", "role": "user"})
        assert token is not None
        assert isinstance(token, str)

    def test_token_contains_correct_payload(self):
        """Test that the token payload contains the expected data."""
        token = create_access_token(data={"sub": "42", "role": "admin"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_token_has_expiration(self):
        """Test that the token includes an expiration claim."""
        token = create_access_token(data={"sub": "1"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert "exp" in payload

    def test_token_expiration_is_in_future(self):
        """Test that the token expiration is set in the future."""
        token = create_access_token(data={"sub": "1"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        assert exp > datetime.now(UTC)

    def test_token_with_wrong_secret_fails(self):
        """Test that decoding with a wrong secret key raises JWTError."""
        token = create_access_token(data={"sub": "1"})
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong-secret-key", algorithms=[settings.ALGORITHM])

    def test_token_with_wrong_algorithm_fails(self):
        """Test that decoding with a wrong algorithm raises JWTError."""
        token = create_access_token(data={"sub": "1"})
        with pytest.raises(JWTError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS384"])

    def test_tampered_token_fails(self):
        """Test that a tampered token fails validation."""
        token = create_access_token(data={"sub": "1"})
        tampered_token = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            jwt.decode(tampered_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    def test_token_preserves_additional_data(self):
        """Test that extra claims are preserved in the token."""
        token = create_access_token(data={"sub": "1", "custom_field": "hello"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["custom_field"] == "hello"
