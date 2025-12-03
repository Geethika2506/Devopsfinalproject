"""Basic API tests for product endpoints."""
from __future__ import annotations

import httpx
import pytest


pytestmark = pytest.mark.anyio("asyncio")


async def test_create_and_list_products(client: httpx.AsyncClient) -> None:
    payload = {
        "title": "Test Backpack",
        "price": 74.5,
        "description": "Sample",
        "category": "bags",
        "image": "https://example.com/image.png",
        "rating": {"rate": 4.2, "count": 17},
    }
    create_resp = await client.post("/products/", json=payload)
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["title"] == payload["title"]
    assert body["price"] == payload["price"]
    assert body["description"] == payload["description"]
    assert body["category"] == payload["category"]
    assert body["image"] == payload["image"]
    assert body["rating"] == payload["rating"]

    list_resp = await client.get("/products/")
    assert list_resp.status_code == 200
    products = list_resp.json()
    assert len(products) == 1
    assert products[0]["title"] == payload["title"]
