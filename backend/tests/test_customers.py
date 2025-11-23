"""Customer endpoint tests."""
from __future__ import annotations

import httpx
import pytest


pytestmark = pytest.mark.anyio("asyncio")


async def test_create_and_fetch_customer(client: httpx.AsyncClient) -> None:
    payload = {"name": "Alice", "email": "alice@example.com"}
    resp = await client.post("/customers/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == payload["email"]

    get_resp = await client.get(f"/customers/{body['id']}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["name"] == payload["name"]

async def test_duplicate_email_fails(client: httpx.AsyncClient) -> None:
    payload = {"name": "Bob", "email": "bob@example.com"}
    first = await client.post("/customers/", json=payload)
    assert first.status_code == 201

    second = await client.post("/customers/", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already registered"
