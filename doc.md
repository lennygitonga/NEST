# NEST — Real Estate Property Management Platform

## What is NEST?

NEST is a multi-tenant SaaS real estate property management platform that connects housing agencies, landlords, and tenants. Agencies manage properties on behalf of landlords, handle tenant applications, collect rent, and manage maintenance requests. NEST takes a 10% commission on all rent collected. Landlords get a read-only dashboard showing their property performance and payouts. Tenants can browse vacant properties, apply for units, pay rent, and file maintenance tickets.

---

## The 4 User Roles

| Role | Description |
|---|---|
| **NEST Admin** | Superuser — oversees all agencies, approves agency registrations, collects 10% commission |
| **Agency** | Signs up and manages properties on behalf of landlords, handles tenants and maintenance |
| **Landlord** | Owns properties, read-only access to performance reports and payout history |
| **Tenant** | Browses listings, applies for units, pays rent, files maintenance tickets |

---

## How Money Flows

```
Tenant pays rent (e.g. KSh 20,000)
        ↓
NEST takes 10% commission = KSh 2,000
        ↓
Agency receives 90% = KSh 18,000
        ↓
Agency pays landlord (minus their own management fee if applicable)
```

Every payment record stores:
- Total amount paid by tenant
- NEST commission (10%)
- Amount after commission
- Agency payout status
- Landlord payout status

---

## Core Features

### 1. User Authentication & Role Management
- Register via email/password or Google OAuth
- Role assigned at registration (Agency, Landlord, Tenant)
- NEST Admin is a superuser created via Django Admin
- JWT token-based session management
- Password reset via email
- Two-Factor Authentication (2FA) via Google Authenticator (TOTP)

### 2. Agency Registration & Verification
- Agencies sign up with their company details
- NEST Admin must approve an agency before they can list properties
- Adds a trust and verification layer to the platform
- Agencies have a profile with name, logo, registration number, and contact details

### 3. Property Listings & Management
- Agencies list and manage properties on behalf of landlords
- Every property is linked to both an Agency (manager) and a Landlord (owner)
- Property types: Residential, Commercial, Short-term Rental
- Vacant properties are publicly visible — no account needed to browse
- Landlord submits a property to an agency; agency accepts and takes over management

### 4. Tenant Applications & Lease Management
- Tenants apply for vacant properties from the public listing page
- Agencies approve or reject applications
- Agencies can also invite tenants directly
- Approved tenants get a formal lease record
- Lease includes start date, end date, and attached lease document (PDF)
- Tenant Credit Scoring — internal score based on payment history shown to agencies

### 5. Maintenance Ticket System
- Tenants file maintenance requests with photos and priority level
- Ticket statuses: Open → In Progress → Resolved
- Agency staff manage all tickets across their properties
- Both agency and tenant communicate through a comment thread inside each ticket

### 6. Rent Payment Tracking & Commission
- Records full payment breakdown (total, NEST cut, agency earnings, landlord payout)
- M-Pesa or Stripe integration for direct payments
- NEST automatically calculates and records 10% commission on every payment
- Agencies see full payment overview across all their properties
- Tenants see their own payment history

### 7. Payout System
- NEST pays agencies (after deducting 10% commission)
- Agencies pay landlords (after deducting their own management fee if applicable)
- Every payout is recorded with status (Pending, Processed, Failed)
- Landlords get notified when rent is collected and when their payout is processed

### 8. Monthly Payout Reports
- Auto-generated monthly summary for each landlord
- Shows total rent collected, NEST commission deducted, and final payout received
- Downloadable as PDF
- Agencies also get a monthly earnings summary

### 9. Landlord Read-Only Dashboard
- Property performance overview
- Occupancy rates
- Total rent collected per property
- Payout history and pending payouts

### 10. Agency Performance Dashboard
- Total properties managed
- Occupancy rate across portfolio
- Total rent collected this month
- Outstanding/overdue payments
- Tenant application pipeline

### 11. Notifications System
- In-app and email notifications for:
  - Agency verification approved/rejected
  - Lease expiry warnings
  - Upcoming payment due dates
  - Maintenance ticket status changes
  - Tenant application approvals/rejections
  - Payout processed confirmations

---

## Backend Architecture

### Style
Decoupled REST API — Django serves only JSON. No HTML templates. Frontend connects separately.

### App Structure

```
NEST/
├── core/               — Project config (settings, URLs, environment)
├── authentication/     — Users, roles, JWT, Google OAuth, 2FA, password reset
├── agencies/           — Agency profiles, verification, performance dashboard
├── properties/         — Property listings, lease management, tenant applications
├── tickets/            — Maintenance tickets and comment threads
├── payments/           — Rent payments, commission calculation, payouts, reports
├── notifications/      — In-app and email notification system
├── manage.py
├── requirements.txt
├── .env
└── .gitignore
```

### Request Flow
```
HTTP Request
    → URL Router (core/urls.py)
    → View / ViewSet (views.py) — checks auth & permissions
    → Serializer (serializers.py) — validates & transforms data
    → Model (models.py) — reads/writes to database
    → JSON Response back to client
```

---

## Database Models

### authentication
- `UserProfile` — role (NEST_ADMIN, AGENCY, LANDLORD, TENANT), phone, photo, ID document, 2FA fields

### agencies
- `Agency` — name, registration number, logo, contact, is_verified, commission_rate
- `AgencyLandlord` — links a landlord to an agency

### properties
- `Property` — agency, landlord, title, type, address, rent, photos, vacancy status
- `PropertyApplication` — tenant, property, status (Pending, Approved, Rejected)
- `Lease` — tenant, property, agency, start date, end date, document

### tickets
- `MaintenanceTicket` — property, reported_by, title, description, priority, status, photo
- `TicketComment` — ticket, author, text, timestamp

### payments
- `RentPayment` — tenant, property, total amount, nest_commission, agency_earnings, date, status
- `Payout` — recipient (agency or landlord), amount, type, status, processed_at
- `TenantCreditScore` — tenant, score, total_payments, late_payments, last_updated

### notifications
- `Notification` — recipient, message, is_read, linked object, created_at

---

## API Endpoints

### Authentication
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | Public | Register a new user |
| POST | `/api/auth/login/` | Public | Login and receive JWT token |
| POST | `/api/auth/token/refresh/` | Public | Refresh JWT token |
| POST | `/api/auth/password-reset/` | Public | Request password reset email |
| POST | `/api/auth/password-reset-confirm/` | Public | Confirm new password |
| POST | `/api/auth/2fa/setup/` | Private | Enable 2FA |
| POST | `/api/auth/2fa/verify/` | Private | Verify 2FA code |
| GET | `/api/auth/google/` | Public | Google OAuth login |

### Agencies
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/agencies/register/` | Public | Agency signs up |
| GET | `/api/agencies/` | NEST Admin | List all agencies |
| PATCH | `/api/agencies/<id>/verify/` | NEST Admin | Approve or reject agency |
| GET | `/api/agencies/<id>/dashboard/` | Agency | Agency performance dashboard |
| POST | `/api/agencies/<id>/landlords/` | Agency | Link a landlord to the agency |

### Properties
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/properties/` | Public | Browse all vacant properties |
| POST | `/api/properties/` | Agency | Create a new property listing |
| GET | `/api/properties/<id>/` | Public | View property details |
| PUT/PATCH | `/api/properties/<id>/` | Agency | Update property details |
| DELETE | `/api/properties/<id>/` | Agency | Delete a property |

### Applications & Leases
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/applications/` | Tenant | Apply for a vacant property |
| GET | `/api/applications/` | Private | Agency sees all; Tenant sees their own |
| PATCH | `/api/applications/<id>/` | Agency | Approve or reject application |
| GET | `/api/leases/` | Private | Agency/Landlord sees all; Tenant sees their own |
| POST | `/api/leases/` | Agency | Create a lease for a tenant |

### Maintenance Tickets
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/tickets/` | Private | Agency sees all; Tenant sees their own |
| POST | `/api/tickets/` | Tenant | File a new maintenance request |
| PATCH | `/api/tickets/<id>/` | Agency | Update ticket status |
| GET | `/api/tickets/<id>/comments/` | Private | View ticket comment thread |
| POST | `/api/tickets/<id>/comments/` | Private | Add a comment to a ticket |

### Payments & Payouts
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/payments/` | Private | Agency/Landlord sees all; Tenant sees their own |
| POST | `/api/payments/` | Tenant | Initiate a rent payment |
| GET | `/api/payouts/` | Private | Agency/Landlord sees their payouts |
| GET | `/api/payments/reports/monthly/` | Agency/Landlord | Download monthly payout report |
| GET | `/api/tenants/<id>/credit-score/` | Agency | View tenant credit score |

### Notifications
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/notifications/` | Private | Fetch all notifications for logged-in user |
| PATCH | `/api/notifications/<id>/` | Private | Mark notification as read |

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.14 | Core programming language |
| Django | Backend web framework |
| Django REST Framework | REST API development |
| SimpleJWT | JWT token authentication |
| django-allauth | Google OAuth integration |
| django-cors-headers | Cross-origin request handling |
| Pillow | Image and photo uploads |
| python-dotenv | Environment variable management |
| SQLite (dev) / PostgreSQL (prod) | Database |
| M-Pesa / Stripe | Payment gateway |
| Postman | API testing |

---

## Commission & Payout Logic

```
Monthly Rent Collected = Sum of all RentPayments in the month

NEST Commission = Monthly Rent Collected × 10%

Agency Earnings = Monthly Rent Collected - NEST Commission

Landlord Payout = Agency Earnings - Agency Management Fee (if applicable)

Tenant Credit Score:
  - Goes up with every on-time payment
  - Goes down with every late or missed payment
  - Visible to agencies when reviewing applications
```

---

## Build Plan

### Thursday — Models
- [x] Project setup complete
- [ ] authentication/models.py
- [ ] agencies/models.py
- [ ] properties/models.py
- [ ] tickets/models.py
- [ ] payments/models.py
- [ ] notifications/models.py
- [ ] Run all migrations
- [ ] Register all models in Django Admin
- [ ] Verify in Django Admin panel

### Friday — API Layer
- [ ] Serializers for all models
- [ ] Views and ViewSets
- [ ] URL endpoints
- [ ] Authentication (JWT + Google OAuth)
- [ ] Permissions (role-based access control)
- [ ] Commission calculation logic
- [ ] Test all endpoints in Postman

---

## Postman Testing Order

| # | Endpoint | Method | What it tests |
|---|---|---|---|
| 1 | `/api/auth/register/` | POST | Register an agency |
| 2 | `/api/auth/register/` | POST | Register a landlord |
| 3 | `/api/auth/register/` | POST | Register a tenant |
| 4 | `/api/auth/login/` | POST | Get JWT token |
| 5 | `/api/agencies/<id>/verify/` | PATCH | Admin approves agency |
| 6 | `/api/properties/` | POST | Agency creates a property |
| 7 | `/api/properties/` | GET | Public listing — no token needed |
| 8 | `/api/applications/` | POST | Tenant applies for a property |
| 9 | `/api/applications/<id>/` | PATCH | Agency approves application |
| 10 | `/api/leases/` | POST | Agency creates a lease |
| 11 | `/api/tickets/` | POST | Tenant files a maintenance ticket |
| 12 | `/api/tickets/<id>/` | PATCH | Agency updates ticket status |
| 13 | `/api/tickets/<id>/comments/` | POST | Both users leave comments |
| 14 | `/api/payments/` | POST | Tenant makes a rent payment |
| 15 | `/api/payouts/` | GET | Agency/Landlord views payouts |
| 16 | `/api/payments/reports/monthly/` | GET | Download monthly report |
| 17 | `/api/notifications/` | GET | Fetch notifications |

---

*Built with Django REST Framework — NEST Backend v1.0*