# AI Clinical Assistant Platform

An AI-powered Clinical Workflow Operating System for doctors, assistants, clinics, chambers, hospitals, and telemedicine — with first-class support for **Bangla medical language**.

---

## Features

| Module | Highlights |
|--------|-----------|
| 👤 **User Roles & RBAC** | 9 roles (Super Admin → Patient), per-role permission enforcement |
| 🔐 **Auth & Security** | JWT access/refresh tokens, TOTP MFA, bcrypt passwords, audit logs |
| 🏥 **Patient Management** | Unique ID (`HSP-DHK-2026-000001`), smart duplicate detection, allergy tracking |
| 📅 **Appointments & Queue** | Token system, emergency priority override, online/follow-up types |
| 🎙️ **AI Voice Intake** | Audio upload → transcription → Bangla NLP → structured clinical history |
| 🧠 **Bangla Medical NLP** | 30+ term dictionary (বুক ধড়ফড় → Palpitation, গ্যাস → GERD) |
| 🩺 **Diagnosis Support** | Differential diagnosis suggestions, red-flag detection, confidence scoring |
| 💊 **Prescription AI** | Voice-to-prescription parsing, drug interaction checks, allergy validation |
| 🔬 **Lab Reports** | Upload, OCR extraction stub, critical alert detection |
| 📊 **Vitals & Triage** | NEWS2 score auto-calculation (Low/Medium/High risk) |
| 📁 **EMR/EHR Timeline** | Full patient timeline, immutable records after finalization |
| 💊 **Pharmacy** | Inventory, expiry tracking, prescription-only dispensing |
| 💳 **Billing** | Invoice, payments, refund approval workflow |
| 📢 **Notifications** | SMS/WhatsApp/push stubs, appointment & medicine reminders |
| 📈 **Analytics** | Disease trends, outbreak detection, doctor performance |
| 🏢 **Multi-tenant SaaS** | Full tenant isolation — Hospital A cannot access Hospital B data |

---

## Tech Stack

- **Backend / API**: Python 3.12 · FastAPI · SQLAlchemy 2
- **Database**: PostgreSQL (SQLite for tests)
- **Auth**: `python-jose` (JWT) · `passlib/bcrypt` · `pyotp` (TOTP)
- **AI stubs**: designed to be replaced with Whisper (STT), GPT / MedGemma / ClinicalBERT
- **Tests**: pytest · pytest-asyncio

---

## Quick Start

### 1. Clone and install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY, etc.
```

### 3. Run the API server

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

### 4. Run tests

```bash
cd backend
pytest tests/ -v
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, startup, router registration
│   ├── config.py            # Settings via pydantic-settings / .env
│   ├── database.py          # SQLAlchemy engine, session, Base, init_db
│   ├── core/
│   │   ├── security.py      # JWT creation/decode, bcrypt, TOTP MFA
│   │   ├── permissions.py   # RBAC definitions (9 roles × permissions)
│   │   └── dependencies.py  # FastAPI get_current_user dependency
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── tenant.py        # Tenant (hospital), TenantSettings
│   │   ├── user.py          # User, Role enum, UserDevice
│   │   ├── patient.py       # Patient, PatientAllergy, MergeRequest
│   │   ├── visit.py         # Visit, Symptom
│   │   ├── prescription.py  # Prescription, PrescriptionItem, DrugInteractionAlert
│   │   ├── lab_report.py    # LabReport, LabResult
│   │   ├── vitals.py        # VitalSigns, NewsScore
│   │   ├── appointment.py   # Appointment, Queue
│   │   ├── audio.py         # AudioRecord, Transcription, TranscriptionSegment, AISummary
│   │   ├── audit.py         # AuditLog
│   │   ├── pharmacy.py      # Medicine, Dispensing
│   │   └── billing.py       # Invoice, Payment
│   ├── schemas/             # Pydantic v2 request/response schemas
│   ├── routers/             # FastAPI routers (one per module)
│   │   ├── auth.py          # /api/v1/auth/*
│   │   ├── users.py         # /api/v1/users/*
│   │   ├── patients.py      # /api/v1/patients/*
│   │   ├── visits.py        # /api/v1/visits/*
│   │   ├── appointments.py  # /api/v1/appointments/*
│   │   ├── audio_intake.py  # /api/v1/audio/*  ← MOST IMPORTANT
│   │   ├── prescriptions.py # /api/v1/prescriptions/*
│   │   ├── lab_reports.py   # /api/v1/lab-reports/*
│   │   ├── vitals.py        # /api/v1/vitals/*
│   │   ├── emr.py           # /api/v1/emr/*
│   │   ├── pharmacy.py      # /api/v1/pharmacy/*
│   │   ├── billing.py       # /api/v1/billing/*
│   │   ├── analytics.py     # /api/v1/analytics/*
│   │   └── notifications.py # /api/v1/notifications/*
│   └── services/
│       ├── ai_service.py            # Bangla NLP, diagnosis, drug interactions
│       ├── auth_service.py          # Login, token management, MFA
│       ├── patient_service.py       # UID generation, duplicate detection
│       ├── prescription_service.py  # Create, sign, interaction checks
│       ├── audit_service.py         # Audit log writer
│       └── notification_service.py  # SMS/push notification stubs
├── tests/
│   ├── conftest.py          # SQLite in-memory DB, test client, fixtures
│   ├── test_auth.py         # Login, MFA, JWT, session management
│   ├── test_patients.py     # Registration, UID format, duplicate detection
│   ├── test_prescriptions.py # Create, sign, drug interaction detection
│   └── test_ai_service.py   # Bangla NLP, diagnosis, red-flag detection
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Key Business Rules

### Role Restrictions
- **Assistant**: CAN create patient visit, record conversation, collect history, upload vitals.  
  CANNOT finalize diagnosis or sign/approve prescription.
- **Doctor**: CAN approve AI summary, add diagnosis, sign prescription, modify AI suggestions.

### Prescription Signing
Prescription approval requires one of: `password` · `biometric` · `OTP`.  
Signed prescriptions cannot be re-signed (HTTP 409).

### Patient Unique ID
Format: `{TENANT_CODE}-{CITY}-{YEAR}-{NNNNNN}`  
Example: `HSP-DHK-2026-000001`  Never reused.

### EMR Immutability
Once a visit is finalized (`doctor_approved_at` set), clinical history fields (`chief_complaint`, `hpi`, `ros`, etc.) are immutable — returns HTTP 403 if modification is attempted.

### Emergency Queue
Appointments flagged `is_emergency=True` receive token `0` and are prepended to the queue.

### Critical Lab Alerts
Automatically flagged as critical when:
- Platelet < 20,000
- Troponin > 0.4
- Glucose < 40 or > 500

### Multi-tenant Isolation
Every query is scoped to `tenant_id`.  
`check_tenant_access()` in `core/permissions.py` enforces cross-tenant access denial (HTTP 403).

---

## AI Pipeline

```
Audio Input
    ↓
Speech-to-Text (Whisper stub)
    ↓
Speaker Identification [PATIENT] / [ASSISTANT] / [DOCTOR]
    ↓
Bangla Medical NLP  (translate_bangla_symptoms)
    ↓
Symptom Extraction  (extract_clinical_history)
    ↓
Differential Diagnosis Suggestions  (suggest_diagnosis)
    ↓
Red-Flag Detection  (detect_red_flags)
    ↓
Prescription Assistance  (parse_voice_prescription)
    ↓
Drug Interaction Check  (check_drug_interactions)
    ↓
Doctor Validation  → visit/approve endpoint
    ↓
Final EMR Record
```

---

## Recommended Rollout (Phased)

| Phase | Focus |
|-------|-------|
| 1 | AI voice intake + Bangla transcription |
| 2 | Medical summary & clinical history |
| 3 | Diagnosis support |
| 4 | Prescription AI + drug interaction |
| 5 | Hospital ERP integration |
