# Flux
**Last-Mile Delivery Orchestration API**

Flux is a production-ready REST API that manages the full lifecycle of a last-mile delivery. It is not a mobile app or a website. It is the infrastructure engine that any frontend, mobile app, or third-party platform can integrate with to handle delivery orchestration.

Built in 30 days as part of the #ENg30DayChallenge · Backend Track.

---

## What Flux Does

Businesses plug into Flux to manage their delivery operations. A sender creates a delivery request, available riders are notified and the first to accept gets the job, and delivery is confirmed through a sequential mutual verification system that requires both the rider and customer to be physically present.

No more informal WhatsApp assignments. No more verbal confirmations with no audit trail.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django + Django REST Framework |
| Database | PostgreSQL (Supabase) |
| Auth | JWT (SimpleJWT) with refresh token rotation |
| Cache & Broker | Redis *(coming soon)* |
| Background Tasks | Celery + Celery Beat *(coming soon)* |
| Deployment | Railway / Render |

---

## System Actors

| Actor | Role |
|-------|------|
| Sender | Creates delivery requests. Tracks status. Cannot see confirmation codes or change delivery state. |
| Rider | Accepts orders. Drives the delivery state machine. Participates in mutual verification on arrival. |
| Customer | Registered user linked to deliveries. Receives their code on rider arrival. Enters rider code to confirm receipt. |
| Admin | Full system access. Can override states and monitor all platform activity. |

---

## Delivery State Machine

Every delivery moves through a fixed sequence. No actor can skip a state or move backwards.

```
PENDING → ASSIGNED → PICKED_UP → IN_TRANSIT → ARRIVED → DELIVERED → COMPLETED
```

| State | Triggered By | Meaning |
|-------|-------------|---------|
| PENDING | System | Order created. No rider yet. |
| ASSIGNED | Rider | First rider to accept the broadcast. |
| ACCEPTED | Rider | First rider to accept the broadcast. |
| PICKED_UP | Rider | Package collected from sender. |
| IN_TRANSIT | Rider | Rider is moving to customer location. |
| ARRIVED | Rider | Rider is at customer location. Codes generated. |
| DELIVERED | Both | Mutual verification complete. |
| COMPLETED | System | Delivery closed. Record is final. |

---

## Mutual Verification System

This is the core trust mechanism in Flux. Delivery cannot be marked complete unless both the rider and customer are physically present and exchange codes.

**How it works:**

1. Rider clicks "I am here" → system generates two codes, one per party
2. Customer receives their code. Rider receives their code.
3. Rider enters the customer's code into Flux first — verified.
4. Customer then enters the rider's code into Flux — verified.
5. Both verified → delivery moves to DELIVERED. Rider is freed up automatically.

Both codes expire after 15 minutes. Neither party can complete delivery alone.

---

## API Endpoints

Base URL: `/api/`

### Authentication

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/auth/register/` | Public | Create account with role |
| POST | `/api/auth/login/` | Public | Get JWT tokens |
| POST | `/api/auth/refresh/` | Public | Rotate refresh token |
| POST | `/api/auth/logout/` | Authenticated | Invalidate refresh token |
| GET | `/api/profile/` | Authenticated | Get role-specific profile details |

### Deliveries

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/deliveries/` | Sender | Create a new delivery request |
| GET | `/api/deliveries/available/` | Rider | List all pending orders available for pickup |
| GET | `/api/deliveries/<order_id>/details/` | All roles | Get details of a specific delivery |
| POST | `/api/deliveries/<order_id>/accept/` | Rider | Accept a pending delivery |
| POST | `/api/deliveries/<order_id>/pickup/` | Rider | Mark package as picked up |
| POST | `/api/deliveries/<order_id>/intransit/` | Rider | Mark delivery as in transit |
| POST | `/api/deliveries/<order_id>/arrive/` | Rider | Mark as arrived and generate verification codes |
| POST | `/api/deliveries/<order_id>/confirm/` | Rider, Customer | Two-step mutual delivery verification |

### Rider Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/rider/orders/` | Rider | List all past and present assigned orders |
| POST | `/api/rider/availability/` | Rider | Toggle online/offline status |

### Sender Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/sender/orders/` | Sender | List all orders created by the sender |
| GET | `/api/sender/orders/<order_id>/details/` | Sender | Get details of a specific order |

### Customer Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/customer/orders/` | Customer | List all orders assigned to the customer |
| GET | `/api/customer/orders/<order_id>/details/` | Customer | Get details of a specific order |

---

## Production Features

### Logging
Every state transition writes a structured log: delivery ID, actor ID, actor role, previous state, new state, timestamp. Complete audit trail on every delivery.

### Rate Limiting *(coming soon)*
- Login: 5 requests per minute per IP
- Delivery creation: 10 requests per hour per Sender
- State transitions: 20 requests per hour per Rider

### Caching — Redis *(coming soon)*
- Rider availability list: 60 seconds, cleared on status change
- Delivery status reads: 30 seconds per delivery ID, cleared on state change
- Admin delivery list: 120 seconds per query

### Background Tasks — Celery *(coming soon)*
- Auto-rebroadcast unaccepted orders after timeout
- Code expiry cleanup after 15 minutes
- No-show rider timeout

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/DatomCode/flux-api.git
cd flux-api/backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

---

## Running Tests

```bash
python manage.py test fluxapi
```

Tests use SQLite locally — no cloud database required.

---

## ERD Design

[View ERD on Google Drive](https://drive.google.com/file/d/1j-tggyK3RoAuAkRDZqTdaPwm6-U2mUcv/view?usp=sharing)

---

## Live Demo

Coming Day 30.

API docs: `/api/docs/`

---

## Author

**Enoch Gbadebo (Datom)**
Backend Developer · Django / DRF / PostgreSQL

[LinkedIn](https://www.linkedin.com/in/gbadeboenoch/) · [GitHub](https://github.com/datom-code)

Built as part of #ENg30DayChallenge · #ENgShipIt

