from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+pg8000://postgres:Vinh2006@localhost:5432/quan_ly_kho"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def test_connection():
    try:
        with engine.connect():
            return {
                "success": True,
                "database": "quan_ly_kho",
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }