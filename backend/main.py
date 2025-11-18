# app/main.py
import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from . import crud, models, schemas
from .database import SessionLocal, engine

# create tables (MVP simple approach)
models.Base.metadata.create_all(bind=engine)

APPINSIGHTS_KEY = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY") or os.getenv("APPINSIGHTS_CONNECTION_STRING")
ENV = os.getenv("ENV", "dev")

# basic logging (stdout, captured by Azure App Service / container logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sddo-mvp")
logger.info(f"Starting sddo-mvp app (ENV={ENV})")

app = FastAPI(title="SDDO Azure MVP", version="0.1")

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return JSONResponse({"status": "ok", "env": ENV})

@app.post("/items", response_model=schemas.Item)
def create_item(item_in: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = crud.create_item(db, item_in)
    logger.info(f"Created item id={item.id} title={item.title}")
    return item

@app.get("/items", response_model=list[schemas.Item])
def list_items(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
