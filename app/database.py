from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from app.core.env_data import DATABASE_URL
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()