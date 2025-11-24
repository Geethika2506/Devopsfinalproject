"""Minimal API key authentication dependency."""
from __future__ import annotations

import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_ENV = "API_KEY"
API_KEY_HEADER = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """Validate an API key only when the env var is configured."""
    expected_key = os.getenv(API_KEY_ENV)
    if not expected_key:
        return None  # No key configured -> allow all requests (dev convenience)

    if api_key == expected_key:
        return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "API key"},
    )
