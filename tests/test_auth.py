"""Unit tests for authentication module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

import pytest
from datetime import timedelta
from jose import jwt, JWTError
from fastapi import HTTPException

import auth
import models


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password(self):
        """Test password hashing produces a hash."""
        password = "mysecretpassword"
        hashed = auth.get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        # Argon2 hashes start with $argon2
        assert hashed.startswith("$argon2")

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt)."""
        password = "mysecretpassword"
        hash1 = auth.get_password_hash(password)
        hash2 = auth.get_password_hash(password)
        
        assert hash1 != hash2  # Different salts

    def test_verify_password_correct(self):
        """Test verifying a correct password."""
        password = "mysecretpassword"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying an incorrect password."""
        password = "mysecretpassword"
        wrong_password = "wrongpassword"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test verifying with empty password."""
        hashed = auth.get_password_hash("realpassword")
        
        assert auth.verify_password("", hashed) is False

    def test_hash_password_long(self):
        """Test hashing a long password (no 72-byte limit with argon2)."""
        # Argon2 doesn't have bcrypt's 72-byte limit
        long_password = "a" * 200
        hashed = auth.get_password_hash(long_password)
        
        assert auth.verify_password(long_password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "123"}
        token = auth.create_access_token(data)
        
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Test creating token with custom expiry."""
        data = {"sub": "123"}
        expires_delta = timedelta(hours=1)
        token = auth.create_access_token(data, expires_delta)
        
        # Decode and verify expiry is set
        decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        assert "exp" in decoded

    def test_token_contains_subject(self):
        """Test token contains the subject claim."""
        user_id = "42"
        token = auth.create_access_token({"sub": user_id})
        
        decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        assert decoded["sub"] == user_id

    def test_token_contains_expiry(self):
        """Test token contains expiry claim."""
        token = auth.create_access_token({"sub": "123"})
        
        decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        assert "exp" in decoded

    def test_token_with_additional_claims(self):
        """Test token can include additional claims."""
        data = {"sub": "123", "role": "admin", "name": "Test"}
        token = auth.create_access_token(data)
        
        decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        assert decoded["sub"] == "123"
        assert decoded["role"] == "admin"
        assert decoded["name"] == "Test"

    def test_invalid_token_signature(self):
        """Test that invalid signature raises error."""
        token = auth.create_access_token({"sub": "123"})
        
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong-secret-key", algorithms=[auth.ALGORITHM])

    def test_expired_token(self):
        """Test that expired token raises error."""
        # Create token that expires immediately
        data = {"sub": "123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = auth.create_access_token(data, expires_delta)
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    def test_get_current_user_valid_token(self, client, test_user):
        """Test getting current user with valid token."""
        # Login to get token
        response = client.post(
            "/auth/login",
            data={"username": test_user.email, "password": "testpassword123"}
        )
        token = response.json()["access_token"]
        
        # Use token to access protected endpoint
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email

    def test_get_current_user_invalid_token(self, client):
        """Test with invalid token returns 401."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

    def test_get_current_user_missing_token(self, client):
        """Test without token returns 401."""
        response = client.get("/auth/me")
        
        assert response.status_code == 401

    def test_get_current_user_malformed_header(self, client):
        """Test with malformed auth header."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "NotBearer token"}
        )
        
        assert response.status_code == 401


class TestAuthConfiguration:
    """Test authentication configuration."""

    def test_secret_key_exists(self):
        """Test that SECRET_KEY is configured."""
        assert auth.SECRET_KEY is not None
        assert len(auth.SECRET_KEY) > 0

    def test_algorithm_is_valid(self):
        """Test that ALGORITHM is a valid JWT algorithm."""
        assert auth.ALGORITHM in ["HS256", "HS384", "HS512", "RS256"]

    def test_token_expire_minutes_is_set(self):
        """Test that token expiration is configured."""
        assert auth.ACCESS_TOKEN_EXPIRE_MINUTES > 0
