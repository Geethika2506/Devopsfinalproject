"""Utility CLI commands for managing the store backend."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import httpx

from . import crud, database, models


FAKESTORE_PRODUCTS_URL = "https://fakestoreapi.com/products"


def fetch_fakestore_products() -> list[dict]:
    response = httpx.get(FAKESTORE_PRODUCTS_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def transform_product(payload: dict) -> dict:
    """Map FakeStore payload to our DB schema."""
    rating = payload.get("rating") or {}
    return {
        "title": payload.get("title", "Untitled"),
        "price": float(payload.get("price") or 0),
        "description": payload.get("description"),
        "category": payload.get("category", "general"),
        "image": payload.get("image"),
        "rating_rate": float(rating.get("rate") or 0),
        "rating_count": int(rating.get("count") or 0),
    }


def seed_products_from_fakestore(limit: int | None = None) -> None:
    database.create_all_tables()
    with database.get_db() as session:
        session.query(models.Product).delete()
        session.commit()
        products = fetch_fakestore_products()
        if limit:
            products = products[:limit]
        for product in products:
            crud.create_product(session, data=transform_product(product))
    print(f"Seeded {len(products)} FakeStore products")


def dump_products(output_path: Path) -> None:
    with database.get_db() as session:
        rows = crud.list_products(session)
        data = [
            {
                "id": row.id,
                "title": row.title,
                "price": row.price,
                "category": row.category,
            }
            for row in rows
        ]
    output_path.write_text(json.dumps(data, indent=2))
    print(f"Wrote {len(data)} products to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Store CLI helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed-fakestore", help="Seed products from FakeStore API")
    seed_parser.add_argument("--limit", type=int, default=None, help="Limit number of products to seed")

    dump_parser = subparsers.add_parser("dump-products", help="Dump products to JSON")
    dump_parser.add_argument("--output", type=Path, default=Path("products.json"))

    args = parser.parse_args()

    if args.command == "seed-fakestore":
        seed_products_from_fakestore(limit=args.limit)
    elif args.command == "dump-products":
        dump_products(args.output)