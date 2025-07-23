import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.database.models import Base

DB_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(DB_URL)

    # Создаем схему в тестовой БД
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS fastapi_schema"))

    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    # Очищаем таблицы перед каждым тестом
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"TRUNCATE TABLE fastapi_schema.{table.name} CASCADE"))

    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()