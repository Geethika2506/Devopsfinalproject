# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_and_get_item():
    payload = {"title": "test item", "description": "created during test"}
    r = client.post("/items", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == payload["title"]
    item_id = data["id"]

    r2 = client.get(f"/items/{item_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == item_id
