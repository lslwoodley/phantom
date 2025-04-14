# 📄 db.py
# 📍 Location: backend/app/db.py
# 🧠 Purpose: Initialize and manage SQLModel database connection for PostgreSQL

from sqlmodel import SQLModel, create_engine, Session
from app.config import get_settings

settings = get_settings()

# PostgreSQL URL structure: postgresql://user:password@host:port/dbname
DATABASE_URL = settings.postgres_url

# Create SQLAlchemy-compatible engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    from app.models.telemetry_model import TelemetryLog
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
