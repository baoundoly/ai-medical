from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Use check_same_thread=False only for SQLite
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a database session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    # Import all models to ensure they are registered
    from app.models import (  # noqa: F401
        User, UserDevice, Patient, PatientAllergy, MergeRequest,
        Visit, Symptom, Prescription, PrescriptionItem, DrugInteractionAlert,
        LabReport, LabResult, VitalSigns, NewsScore, Appointment, Queue,
        AudioRecord, Transcription, TranscriptionSegment, AISummary,
        AuditLog, Medicine, Dispensing, Invoice, Payment, Tenant, TenantSettings,
    )
    Base.metadata.create_all(bind=engine)
