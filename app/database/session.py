from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/upload_data"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"options": "-csearch_path=fastapi_schema"}
)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()