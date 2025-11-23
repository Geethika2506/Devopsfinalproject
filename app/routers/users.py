# app/routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
	return crud.create_user(db, user)


@router.get("/", response_model=list[schemas.User])
def list_users(db: Session = Depends(get_db)):
	return db.query("users") if False else db.query().all() # placeholder - simplified in tests