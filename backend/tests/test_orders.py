"""Order endpoint tests."""
from __future__ import annotations

import httpx
import pytest


pytestmark = pytest.mark.anyio("asyncio")


async def _create_product(
    client: httpx.AsyncClient, name: str = "Widget", price: float = 9.99
) -> dict:
    payload = {"name": name, "price": price, "description": "Test"}
    resp = await client.post("/products/", json=payload)
    assert resp.status_code == 201
    return resp.json()


async def _create_customer(
    client: httpx.AsyncClient, name: str = "User", email: str = "user@example.com"
) -> dict:
    payload = {"name": name, "email": email}
    resp = await client.post("/customers/", json=payload)
    assert resp.status_code == 201
    return resp.json()


async def test_create_order_success(client: httpx.AsyncClient) -> None:
    customer = await _create_customer(client, "Charlie", "charlie@example.com")
    product = await _create_product(client, "Camera", 199.0)

    payload = {
        "customer_id": customer["id"],
        "product_id": product["id"],
        "quantity": 2,
    }
    resp = await client.post("/orders/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["quantity"] == 2

    get_resp = await client.get(f"/orders/{body['id']}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["customer_id"] == customer["id"]
    assert fetched["product_id"] == product["id"]


async def test_create_order_missing_customer(client: httpx.AsyncClient) -> None:
    product = await _create_product(client)
    resp = await client.post(
        "/orders/",
        json={"customer_id": 9999, "product_id": product["id"], "quantity": 1},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Customer not found"


async def test_create_order_missing_product(client: httpx.AsyncClient) -> None:
    customer = await _create_customer(client)
    resp = await client.post(
        "/orders/",
        json={"customer_id": customer["id"], "product_id": 8888, "quantity": 1},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"
