from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from ..core.config import settings

os.makedirs(settings.steve_runtime_dir, exist_ok=True)
DATABASE_URL = f"sqlite:///{settings.steve_runtime_dir}/stm.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
