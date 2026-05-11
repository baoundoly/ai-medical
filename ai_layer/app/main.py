from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import (
    analytics,
    appointments,
    audio_intake,
    auth,
    billing,
    emr,
    lab_reports,
    notifications,
    patients,
    pharmacy,
    prescriptions,
    users,
    visits,
    vitals,
)

app = FastAPI(
    title="AI Clinical Assistant Platform",
    description="Multi-tenant AI-powered clinical management system with Bangla NLP support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# Include all routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(visits.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(prescriptions.router, prefix="/api/v1")
app.include_router(lab_reports.router, prefix="/api/v1")
app.include_router(vitals.router, prefix="/api/v1")
app.include_router(audio_intake.router, prefix="/api/v1")
app.include_router(emr.router, prefix="/api/v1")
app.include_router(pharmacy.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
