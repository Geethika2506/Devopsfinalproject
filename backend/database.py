# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # e.g. mssql+pyodbc://user:password@server:1433/databasename?driver=ODBC+Driver+18+for+SQL+Server
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # fallback local sqlite for MVP/tests
    sqlite_url = "sqlite:///./data.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
