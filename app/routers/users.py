from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import schemas, crud
from app.database import get_db
from app.auth import create_access_token, verify_password


router = APIRouter()

@router.post("/")
def create_user(user: schemas.UserCreate):
    return crud.create_user(user)


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
	existing = crud.get_user_by_email(db, user.email)
	if existing:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
	u = crud.create_user(db, user)
	return u


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = crud.get_user_by_email(db, form_data.username)
	if not user or not verify_password(form_data.password, user.password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password"
		)
	access_token = create_access_token({"sub": user.email, "role": user.role})
	return {"access_token": access_token, "token_type": "bearer"}