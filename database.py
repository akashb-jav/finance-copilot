from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This creates (or connects to) a file called finance.db in your project folder
DATABASE_URL = "sqlite:///./finance.db"

# Engine is the actual connection to the database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is what you use to talk to the database (read/write)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is what your models (tables) will inherit from
Base = declarative_base()

# This function gives you a database session and closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()