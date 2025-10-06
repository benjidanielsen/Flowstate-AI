from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

# Use connection pooling with QueuePool for better performance
DATABASE_URL = "postgresql+psycopg2://user:password@localhost/flowstate_db"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Adjust pool size based on load
    max_overflow=10,        # Allow some overflow connections
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=1800       # Recycle connections every 30 minutes
)

# Use scoped_session to ensure thread safety in multi-threaded environments
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()