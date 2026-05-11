# AI Clinical Assistant Platform

An AI-powered Clinical Workflow Operating System for doctors, assistants, clinics, chambers, hospitals, and telemedicine — with first-class support for **Bangla medical language**.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
│  ┌────────────────┐          ┌──────────────────────────┐   │
│  │  Flutter App   │          │     React Web App        │   │
│  │  (Mobile iOS/  │          │  (Vite + TypeScript +    │   │
│  │   Android)     │          │   Tailwind CSS)          │   │
│  └───────┬────────┘          └───────────┬──────────────┘   │
└──────────┼────────────────────────────────┼─────────────────┘
           │  REST / JWT Bearer             │
           ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│              ASP.NET Core 8 API Backend                     │
│  Controllers → Services → EF Core → MS SQL Server          │
│  Modules: Auth, Patients, Visits, Appointments,             │
│           Prescriptions, Lab Reports, Vitals, EMR,          │
│           Pharmacy, Billing, Analytics, Notifications       │
└───────────────────────────────┬─────────────────────────────┘
                                │  HTTP (internal)
                                ▼
┌─────────────────────────────────────────────────────────────┐
│             Python FastAPI AI Layer                         │
│  • Bangla speech transcription (Whisper stub)              │
│  • Bangla medical NLP (30+ term dictionary)                 │
│  • Differential diagnosis suggestions                       │
│  • Drug interaction checks                                  │
│  • NEWS2 vitals scoring                                     │
│  • Critical lab alert detection                             │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────┐
│   Microsoft SQL Server   │
│   (via EF Core + MSSQL)  │
└──────────────────────────┘
```

---

## Repository Structure

```
ai-medical/
├── dotnet_backend/        ← ASP.NET Core 8 API (primary backend)
├── ai_layer/              ← Python FastAPI AI microservice
├── web_frontend/          ← React + Vite + TypeScript web app
├── mobile_app/            ← Flutter mobile app (iOS + Android)
└── backend/               ← (legacy) original Python FastAPI backend
```

---

## Components

### 1. ASP.NET Core Backend (`dotnet_backend/`)

**Tech:** .NET 8, EF Core 8, SQL Server, JWT Bearer, BCrypt, Swagger

#### Quick Start
```bash
cd dotnet_backend/src/AIMedical.Api
# Update connection string in appsettings.json
dotnet ef database update    # run migrations
dotnet run                   # starts on http://localhost:5000
```

#### Run tests
```bash
cd dotnet_backend
dotnet test AIMedical.sln
```

#### Swagger UI
Open http://localhost:5000/swagger when running in Development mode.

#### Key features
| Feature | Detail |
|---------|--------|
| Authentication | JWT Bearer + BCrypt password hashing |
| Authorization | 9 roles (SuperAdmin → Patient), role guards on controllers |
| Patient IDs | Format: `HSP-DHK-2026-000001` — never reused |
| Prescription signing | Doctor role required; stores HMAC signature hash |
| Audit logging | AuditMiddleware logs every mutation with user/IP/timestamp |
| Multi-tenant | All queries filtered by `tenantId` claim from JWT |
| AI integration | `AiService` HTTP client calls Python AI layer |
| EMR immutability | Visits locked after doctor approval |

---

### 2. Python AI Layer (`ai_layer/`)

**Tech:** Python 3.12, FastAPI, SQLAlchemy, Pydantic v2

#### Quick Start
```bash
cd ai_layer
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

#### Run tests
```bash
cd ai_layer
pytest tests/ -v
```

#### AI capabilities
| Module | Description |
|--------|-------------|
| Bangla NLP | 30+ medical term dictionary (বুক ধড়ফড় → Palpitation) |
| Transcription | Whisper-compatible stub — replace with real Whisper/STT |
| Diagnosis | Rule-based differential diagnosis suggestions |
| Red-flag detection | Detects chest pain, stroke, sepsis keywords |
| Drug interactions | 8 known dangerous pairs (warfarin+aspirin, etc.) |
| NEWS2 scoring | Standard early-warning score from vitals |
| Critical labs | Auto-detects critical platelet/troponin/glucose values |

---

### 3. React Web App (`web_frontend/`)

**Tech:** React 18, TypeScript, Vite, Tailwind CSS, React Router v6, Axios, Recharts

#### Quick Start
```bash
cd web_frontend
npm install
npm run dev    # starts on http://localhost:3000
```

#### Build for production
```bash
npm run build
```

#### Pages
| Route | Page | Roles |
|-------|------|-------|
| `/login` | Login | All |
| `/dashboard` | Dashboard with stats | All |
| `/patients` | Patient list + registration | Doctor/Assistant/Receptionist |
| `/patients/:id` | Patient detail (tabbed) | Doctor/Assistant |
| `/visits` | Visit list | Doctor/Assistant |
| `/visits/:id` | Visit detail + approve | Doctor |
| `/appointments` | Queue + booking | All |
| `/prescriptions` | Prescriptions + sign | Doctor |
| `/emr/:id` | Full EMR timeline | Doctor |
| `/analytics` | Charts + metrics | Admin/Doctor |

---

### 4. Flutter Mobile App (`mobile_app/`)

**Tech:** Flutter 3.22, Dart 3.4, Provider, GoRouter, Dio, flutter_secure_storage

#### Quick Start
```bash
cd mobile_app
flutter pub get
flutter run    # connect a device or emulator first
```

#### Supported platforms
- Android (minSdk 21)
- iOS (coming soon — no iOS-specific config yet)

#### App features
| Screen | Features |
|--------|---------|
| Login | Email/password, JWT stored in secure storage |
| Dashboard | Stats cards, recent appointments, bottom nav |
| Patients | Search, list, FAB to register, pull-to-refresh |
| Patient Detail | Info + tabs: Visits, Prescriptions, Labs, Vitals |
| Visits | Status filters, list, create new visit |
| Visit Detail | AI Summary box, Approve button (Doctor only) |
| Appointments | Token queue grid, emergency badges, booking |
| Prescriptions | Medicine items, drug interaction warnings, sign button |
| EMR Timeline | Color-coded event timeline |

---

## Database (MS SQL Server)

The ASP.NET Core backend uses **EF Core 8** with the SQL Server provider.

#### Setup
1. Install SQL Server (or use Docker: `docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123!" -p 1433:1433 mcr.microsoft.com/mssql/server:2022-latest`)
2. Update `dotnet_backend/src/AIMedical.Api/appsettings.json`:
   ```json
   "ConnectionStrings": {
     "DefaultConnection": "Server=localhost;Database=AIMedical;User Id=sa;Password=YourPassword123!;TrustServerCertificate=True;"
   }
   ```
3. Run migrations: `dotnet ef database update`

#### Core tables
`Tenants`, `Users`, `Patients`, `Visits`, `Appointments`, `Prescriptions`, `PrescriptionItems`, `LabReports`, `VitalSigns`, `NewsScores`, `AuditLogs`, `Medicines`, `Invoices`

---

## User Roles & Permissions

| Role | Capabilities |
|------|-------------|
| SuperAdmin | Full access to all tenants |
| HospitalAdmin | Manage own tenant |
| Doctor | Approve visits, sign prescriptions, add diagnosis |
| Assistant | Create visits, record history, upload vitals (cannot finalize) |
| Receptionist | Patient registration, appointments |
| Nurse | Record vitals |
| LabTechnician | Upload lab reports |
| Pharmacist | View prescriptions, manage inventory |
| Patient | View own records |

---

## AI Pipeline

```
Audio Input
    ↓
Speech-to-Text (Whisper stub → replace with real model)
    ↓
Speaker Identification [PATIENT] / [ASSISTANT] / [DOCTOR]
    ↓
Bangla Medical NLP (ai_layer/app/services/ai_service.py)
    ↓
Symptom Extraction
    ↓
Differential Diagnosis Suggestions
    ↓
Drug Interaction Check
    ↓
Doctor Validation → /api/visits/{id}/approve
    ↓
Final EMR Record (immutable)
```

---

## Recommended Rollout (Phased)

| Phase | Focus | Components |
|-------|-------|-----------|
| 1 | Auth + Patient management | dotnet_backend + web_frontend login/patients |
| 2 | AI voice intake + transcription | ai_layer + mobile_app recording |
| 3 | Medical summary + diagnosis support | ai_layer NLP + web_frontend visits |
| 4 | Prescription AI + drug interactions | dotnet_backend prescriptions + mobile_app |
| 5 | Hospital ERP + analytics | billing + analytics dashboards |

---

## Environment Variables

### ASP.NET Core (`dotnet_backend/src/AIMedical.Api/appsettings.json`)
```json
{
  "ConnectionStrings": { "DefaultConnection": "..." },
  "JwtSettings": { "SecretKey": "...", "Issuer": "AIMedical", "Audience": "AIMedicalUsers", "ExpiryMinutes": 60 },
  "AiLayerUrl": "http://localhost:8000"
}
```

### Python AI Layer (`ai_layer/.env`)
```
DATABASE_URL=mssql+pyodbc://...
SECRET_KEY=your-secret-key
```

### React Web (`web_frontend/.env`)
```
VITE_API_URL=http://localhost:5000
```

### Flutter Mobile (`mobile_app/lib/core/constants.dart`)
```dart
static const String baseUrl = 'http://10.0.2.2:5000/api';  // Android emulator
```


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
