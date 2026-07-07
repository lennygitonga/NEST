# NEST — Property Management Platform

NEST is a multi-tenant SaaS real estate property management platform connecting agencies, landlords, and tenants under one roof. Agencies list and manage properties on behalf of landlords, tenants browse and apply for properties, and NEST takes a configurable commission on every rent payment processed through the platform.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Overview](#api-overview)
- [User Roles](#user-roles)
- [Key Features](#key-features)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## Overview

NEST is built as a capstone project at Zindua School, Nairobi. It demonstrates a production-quality full-stack SaaS architecture with:

- Role-based access control across four user types
- JWT authentication with refresh token rotation
- Google OAuth sign-in
- AI-powered features via Groq (lease summaries, ticket triage, payment analytics, invoice generation)
- PDF generation for receipts and invoices via ReportLab
- File storage on Cloudinary
- A 10% commission model automatically calculated on every rent payment

---

## Architecture

```
┌─────────────────────────────────────────┐
│              React Frontend             │
│  Vite · Zustand · Tailwind v4 · Framer  │
└────────────────────┬────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────┐
│           Django REST Framework         │
│  8 apps · 79 endpoints · SimpleJWT      │
└────────────────────┬────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
   ┌──────▼──────┐    ┌────────▼────────┐
   │  PostgreSQL  │    │   Cloudinary    │
   │  (Railway)  │    │  (File Storage) │
   └─────────────┘    └─────────────────┘
```

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Framework | Django 6.0.5 + Django REST Framework |
| Language | Python 3.14 |
| Authentication | SimpleJWT + django-allauth (Google OAuth) |
| AI | Groq API — llama-3.3-70b-versatile |
| PDF Generation | ReportLab |
| File Storage | Cloudinary |
| Database (prod) | PostgreSQL via Railway |
| Database (local) | SQLite |
| TOTP / 2FA | pyotp |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + Vite |
| State Management | Zustand (with localStorage persistence) |
| Styling | Tailwind CSS v4 |
| Animations | Framer Motion |
| HTTP Client | Axios (with JWT refresh interceptor) |
| Routing | React Router v6 |
| Charts | Recharts |
| 3D (planned) | React Three Fiber + Three.js + Spline |

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- PostgreSQL (for production) or SQLite (local)
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/lennygitonga/NEST.git
cd NEST

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Create a NEST Admin account
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.create_user(
    username='admin@nest.com',
    email='admin@nest.com',
    password='your-secure-password',
    first_name='NEST',
    last_name='Admin'
)
user.profile.role = 'NEST_ADMIN'
user.profile.is_email_verified = True
user.profile.save()
print('NEST Admin created.')
"

# Start the development server
python manage.py runserver
```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

---

## Environment Variables

Create a `.env` file in the project root with the following:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

# Database (leave blank for SQLite in development)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Groq AI
GROQ_API_KEY=your-groq-api-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# CORS / CSRF (comma-separated origins for production)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

---

## API Overview

The backend exposes **79 endpoints** across **8 Django apps**, all mounted under `/api/`.

| App | Prefix | Description |
|---|---|---|
| `authentication` | `/api/auth/` | Register, login, JWT, email verification, 2FA, Google OAuth, profile, password/email change, account deletion |
| `agencies` | `/api/agencies/` | Agency registration, verification, dashboard, landlord management, tenant listing |
| `properties` | `/api/properties/` | Property listings, images, documents, applications, leases, AI lease summaries |
| `tickets` | `/api/tickets/` | Maintenance tickets with AI auto-priority triage, comment threads |
| `payments` | `/api/payments/` | Rent payments, invoices, receipts, PDF downloads, AI analytics, tenant credit scoring, monthly reports |
| `notifications` | `/api/notifications/` | List, mark read, mark all read, delete |
| `terms` | `/api/terms/` | Versioned Terms and Conditions, acceptance tracking |
| `moderation` | `/api/moderation/` | Ban/unban users, suspend/unsuspend agencies, warnings, fraud reports, ban appeals, audit log |

### Authentication Flow

```
POST /api/auth/register/         — Register (TENANT, LANDLORD, AGENCY)
POST /api/auth/login/            — Login with email + password
POST /api/auth/google-login/     — Login or register with Google ID token
POST /api/auth/verify-email/     — Verify email with 6-digit code
POST /api/auth/token/refresh/    — Refresh JWT access token
POST /api/auth/2fa/setup/        — Begin 2FA setup (returns TOTP secret + QR URI)
POST /api/auth/2fa/verify-setup/ — Confirm 2FA with a code
POST /api/auth/2fa/verify-login/ — Complete login when 2FA is enabled
```

---

## User Roles

NEST has four distinct roles, each with a separate frontend experience:

### TENANT
Browses published properties, submits applications, views their lease (with AI summary), files maintenance tickets, pays rent, downloads receipts and invoices, and manages their profile.

### LANDLORD
Read-only view of properties listed under their name, active leases, maintenance tickets, and rent payments. Property management is handled by their linked agency.

### AGENCY
Full management dashboard — list properties on behalf of landlords, review and approve/reject applications, create leases, manage maintenance tickets, create and send invoices, view payment analytics, and manage linked landlords and tenants.

### NEST ADMIN
Platform-wide oversight — verify or reject agencies, suspend/unsuspend agencies, adjust commission rates, ban/warn/delete users, review ban appeals and fraud reports, view the full audit log, manage Terms and Conditions, and view platform-wide payment analytics.

> **Note:** NEST_ADMIN accounts cannot be created through the public registration flow. They must be created via the Django shell or Django admin panel.

---

## Key Features

### AI Integration (Groq — llama-3.3-70b-versatile)

| Feature | Endpoint | Description |
|---|---|---|
| Lease summary | `GET /api/properties/leases/:id/summary/` | Explains a lease agreement in plain English for tenants |
| Ticket triage | `POST /api/tickets/` | Auto-classifies ticket priority (LOW/MEDIUM/HIGH/URGENT) from the description |
| Payment analytics | `GET /api/payments/analytics/` | Role-aware AI insight on payment and portfolio data |
| Invoice summary | `POST /api/payments/invoices/create/` | Generates a friendly explanation of a new invoice for the tenant |
| Receipt confirmation | `GET /api/payments/:id/receipt/` | Writes a warm one-sentence confirmation message for a payment receipt |

### Commission Model

Every rent payment automatically calculates:
- `nest_commission = total_amount × (agency.commission_rate / 100)`
- `agency_earnings = total_amount - nest_commission`

The default commission rate is 10%. NEST Admin can penalize agencies by adjusting their rate.

### PDF Generation

- Payment receipts — `GET /api/payments/:id/receipt/download/`
- Invoices — `GET /api/payments/invoices/:id/download/`

Both are generated on-demand with ReportLab and require authentication (JWT token in the `Authorization` header).

### Email Verification

On registration, a 6-digit code is sent to the user's email. The code expires after 15 minutes. Google OAuth users are automatically verified since Google has already confirmed their email.

### Two-Factor Authentication

TOTP-based 2FA using pyotp. On setup, the backend returns a secret key and a provisioning URI (compatible with Google Authenticator, Microsoft Authenticator, etc.). Login returns a `2fa_required` status with a UID, which is then used to complete login with a valid TOTP code.

### Ban Appeal System

Banned users can submit an appeal at `POST /api/moderation/appeals/submit/` without authentication. NEST Admin reviews appeals and can approve (which automatically unbans the user) or dismiss them. The outcome is emailed to the user.

---

## Deployment

The backend is deployed on **Railway** with a PostgreSQL addon.

### Railway Start Command

```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

### Important Settings Notes

- `INSTALLED_APPS` order matters: `django.contrib.staticfiles` must come **before** `cloudinary_storage` and `cloudinary`, or `collectstatic` will silently copy zero files.
- `CSRF_TRUSTED_ORIGINS` is built from an env var split on commas — guard against empty strings.
- `DATABASE_URL` is automatically injected by Railway's PostgreSQL addon.

### Live Backend

`https://web-production-6bf6f.up.railway.app`

---

## Project Structure

```
NEST/
├── core/                  # Django project settings, URLs, WSGI
│   ├── settings.py
│   ├── urls.py
│   └── ai_utils.py        # Groq helper
├── authentication/        # Auth, profile, JWT, 2FA, Google OAuth
├── agencies/              # Agency model, dashboard, landlord links
├── properties/            # Properties, applications, leases
├── tickets/               # Maintenance tickets, comments
├── payments/              # Rent payments, invoices, receipts, analytics
├── notifications/         # In-app notifications
├── terms/                 # Terms and Conditions versioning
├── moderation/            # Bans, warnings, fraud, audit log
├── requirements.txt
└── manage.py
```

---

## Frontend Repository

The React frontend is maintained in a separate repository: `NEST-frontend`

Built with Vite, Zustand, Tailwind CSS v4, and Framer Motion. Role-based routing directs each user type to their own dashboard and page set after login.

---

## Author

**Lenny Gitonga**
Zindua School — Nairobi