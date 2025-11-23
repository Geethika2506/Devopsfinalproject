# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.services.external_products import fetch_external_products


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return crud.list_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
	p = crud.get_product(db, product_id)
	if not p:
		raise HTTPException(status_code=404, detail="Product not found")
	return p


@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
	return crud.create_product(db, product)


@router.get("/external")
def external_products():
	"""Return products from FakeStoreAPI (no auth). Useful for demo and seeding."""
	return fetch_external_products()


@router.post("/import-external", response_model=list[schemas.Product])
def import_external(db: Session = Depends(get_db)):
	data = fetch_external_products()
	created = []
	for item in data:
		p = schemas.ProductCreate(title=item.get('title'), description=item.get('description'), price=float(item.get('price', 0)), image_url=item.get('image'))
		created.append(crud.create_product(db, p))
	return created