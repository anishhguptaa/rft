# core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create the SQLAlchemy engine
# The engine is the starting point for any SQLAlchemy application.
# It's the 'home base' for the actual database and its DBAPI.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Checks connections for liveness before handing them out.
    pool_recycle=3600    # Recycle connections after 1 hour
)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
# The class itself is not a session yet, but when we call SessionLocal(),
# it will create a new session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that creates a new SQLAlchemy session for each request.
    The session is closed automatically after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()