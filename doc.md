# NEST — Real Estate Property Management Platform

## What is NEST?

NEST is a full-stack real estate property management platform that streamlines the relationship between landlords and tenants. Landlords can list and manage properties, handle tenant applications, track rent payments, and manage maintenance requests. Tenants can browse vacant properties, apply for units, file maintenance tickets, and communicate directly with their landlord through the platform.

---

## User Roles

| Role | Description |
|---|---|
| **Landlord** | Lists and manages properties, approves tenant applications, tracks payments, handles maintenance |
| **Tenant** | Browses properties, applies for units, pays rent, files maintenance tickets |

Roles are assigned at registration and control access across the entire platform.

---

## Core Features

### 1. User Authentication & Role Management
- Register via email/password or Google OAuth
- Role selection at signup (Landlord or Tenant)
- JWT token-based session management
- Password reset via email
- Two-Factor Authentication (2FA) via Google Authenticator (TOTP)

### 2. Property Listings & Management
- Landlords can create, update, and delete property listings
- Property types: Residential, Commercial, Short-term Rental
- Each listing includes photos, documents, pricing, and vacancy status
- Vacant properties are publicly visible — no account needed to browse

### 3. Tenant Applications & Lease Management
- Tenants can apply for vacant properties from the public listing page
- Landlords can approve or reject applications
- Landlords can also invite tenants directly
- Approved tenants get a formal lease record linking them to the property
- Lease includes start date, end date, and attached lease document (PDF)

### 4. Maintenance Ticket System
- Tenants file maintenance requests with photos and priority level
- Ticket statuses: Open → In Progress → Resolved
- Landlords manage all tickets across their properties
- Both parties communicate through a comment thread inside each ticket

### 5. Rent Payment Tracking
- Records rent payments (amount, date, status)
- M-Pesa or Stripe integration for direct payments
- Landlords see a full payment overview across all properties
- Tenants see their own payment history

### 6. Notifications System
- In-app and email notifications for:
  - Lease expiry warnings
  - Upcoming payment due dates
  - Maintenance ticket status changes
  - Tenant application approvals/rejections

### 7. Landlord Dashboard
- Vacant vs occupied units count
- Leases expiring within 30 days
- Open maintenance tickets
- Recent payments received

### 8. Tenant Portal
- Active lease details
- Current rent status
- Filed maintenance tickets and their progress
- Personal notifications

---

## Backend Architecture

### Style
Decoupled REST API — Django serves only JSON. No HTML templates. Frontend connects separately.

### App Structure

```
NEST/
├── core/               — Project config (settings, URLs, environment)
├── authentication/     — Users, roles, JWT, Google OAuth, 2FA, password reset
├── properties/         — Property listings, lease management, tenant applications
├── tickets/            — Maintenance tickets and comment threads
├── payments/           — Rent payment tracking and payment gateway integration
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

### Properties
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/properties/` | Public | Browse all vacant properties |
| POST | `/api/properties/` | Landlord | Create a new property listing |
| GET | `/api/properties/<id>/` | Public | View property details |
| PUT/PATCH | `/api/properties/<id>/` | Landlord | Update property details |
| DELETE | `/api/properties/<id>/` | Landlord | Delete a property |

### Leases
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/leases/` | Private | Landlord sees all leases; Tenant sees their own |
| POST | `/api/leases/` | Landlord | Create a lease for a tenant |
| GET | `/api/leases/<id>/` | Private | View lease details |

### Applications
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/applications/` | Tenant | Apply for a vacant property |
| GET | `/api/applications/` | Private | Landlord sees all; Tenant sees their own |
| PATCH | `/api/applications/<id>/` | Landlord | Approve or reject an application |

### Maintenance Tickets
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/tickets/` | Private | Landlord sees all; Tenant sees their own |
| POST | `/api/tickets/` | Tenant | File a new maintenance request |
| PATCH | `/api/tickets/<id>/` | Landlord | Update ticket status |
| GET | `/api/tickets/<id>/comments/` | Private | View ticket comment thread |
| POST | `/api/tickets/<id>/comments/` | Private | Add a comment to a ticket |

### Payments
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/payments/` | Private | Landlord sees all; Tenant sees their own |
| POST | `/api/payments/` | Tenant | Record/initiate a rent payment |

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

## Build Plan

### Thursday — Foundation
- [x] Project setup, virtual environment, folder structure
- [x] Dependencies installed
- [x] Settings configured (JWT, CORS, allauth, media)
- [x] `.env` and `.gitignore` set up
- [x] Migrations run
- [x] Superuser created
- [ ] Build all models across all 5 apps
- [ ] Run migrations for custom models
- [ ] Register models in Django Admin

### Friday — API Layer
- [ ] Write serializers for all models
- [ ] Build views and ViewSets
- [ ] Configure all URL endpoints
- [ ] Implement authentication (JWT + Google OAuth)
- [ ] Set up permissions (Landlord vs Tenant access control)
- [ ] Test all endpoints in Postman

---

## Postman Testing Order

| # | Endpoint | Method | What it tests |
|---|---|---|---|
| 1 | `/api/auth/register/` | POST | Create a landlord account |
| 2 | `/api/auth/register/` | POST | Create a tenant account |
| 3 | `/api/auth/login/` | POST | Get JWT token |
| 4 | `/api/properties/` | POST | Landlord creates a property |
| 5 | `/api/properties/` | GET | Public listing — no token needed |
| 6 | `/api/applications/` | POST | Tenant applies for a property |
| 7 | `/api/applications/<id>/` | PATCH | Landlord approves application |
| 8 | `/api/leases/` | POST | Landlord creates a lease |
| 9 | `/api/tickets/` | POST | Tenant files a maintenance ticket |
| 10 | `/api/tickets/<id>/` | PATCH | Landlord updates ticket status |
| 11 | `/api/tickets/<id>/comments/` | POST | Both users leave comments |
| 12 | `/api/payments/` | POST | Record a rent payment |
| 13 | `/api/notifications/` | GET | Fetch notifications |

---

*Built with Django REST Framework — NEST Backend v1.0*