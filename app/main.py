# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import products, users, cart, orders


# create tables
Base.metada