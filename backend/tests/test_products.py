"""Basic API tests for product endpoints."""
from __future__ import annotations

import httpx
import pytest


pytestmark = pytest.mark.anyio("asyncio")


async def test_create_and_list_products(client: httpx.AsyncClient) -> None:
    payload = {"name": "Test Widget", "price": 19.99, "description": "Sample"}
    create_resp = await client.post("/products/", json=payload)
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["name"] == payload["name"]
    assert body["price"] == payload["price"]
    assert body["description"] == payload["description"]

    list_resp = await client.get("/products/")
    assert list_resp.status_code == 200
    products = list_resp.json()
    assert len(products) == 1
    assert products[0]["name"] == payload["name"]
