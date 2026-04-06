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

- **Framework:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Cache & Broker:** Redis
- **Background Tasks:** Celery + Celery Beat
- **Auth:** JWT (SimpleJWT) with refresh token rotation
- **Tests:** pytest-django + factory_boy
- **Deployment:** Railway / Render

---

## System Actors

| Actor        | Role                                                                                                          |
| ------------ | ------------------------------------------------------------------------------------------------------------- |
| **Sender**   | Creates delivery requests. Tracks status. Cannot see confirmation codes or change delivery state.             |
| **Rider**    | Accepts or rejects orders. Drives the delivery state machine. Participates in mutual verification on arrival. |
| **Customer** | Registered user linked to deliveries. Receives Code A on rider arrival. Enters Code B to confirm receipt.     |
| **Admin**    | Full system access. Can assign riders, override states, and monitor all platform activity.                    |

---

## Delivery State Machine

Every delivery moves through a fixed sequence. No actor can skip a state or move backwards.

```
PENDING → ASSIGNED → ACCEPTED → PICKED_UP → IN_TRANSIT → ARRIVED → DELIVERED → COMPLETED
```

| State      | Triggered By | Meaning                                         |
| ---------- | ------------ | ----------------------------------------------- |
| PENDING    | System       | Order created. No rider yet.                    |
| ASSIGNED   | Rider        | First rider to accept the broadcast.            |
| ACCEPTED   | Rider        | Rider confirms they are taking the job.         |
| PICKED_UP  | Rider        | Package collected from sender.                  |
| IN_TRANSIT | Rider        | Rider is moving to customer location.           |
| ARRIVED    | Rider        | Rider is at customer location. Codes generated. |
| DELIVERED  | Both         | Mutual verification complete.                   |
| COMPLETED  | System       | Delivery closed. Record is final.               |

---

## Mutual Verification System

This is the core trust mechanism in Flux. Delivery cannot be marked complete unless both the rider and customer are physically present and exchange codes.

**How it works:**

1. Rider clicks "I am here" → system generates Code A and Code B
2. Code A is sent to the customer. Code B is held by the system.
3. Customer reads Code A to the rider. Rider enters it into Flux.
4. Code A is verified → Code B is revealed to the rider only.
5. Rider reads Code B to the customer. Customer enters it into Flux.
6. Both verified → delivery moves to DELIVERED.

Both codes expire after **10 minutes**. Neither party can complete delivery alone.

---

## API Endpoints

### Authentication

| Method | Endpoint              | Access        | Description              |
| ------ | --------------------- | ------------- | ------------------------ |
| POST   | `/api/auth/register/` | Public        | Create account with role |
| POST   | `/api/auth/login/`    | Public        | Get JWT tokens           |
| POST   | `/api/auth/refresh/`  | Public        | Rotate refresh token     |
| POST   | `/api/auth/logout/`   | Authenticated | Invalidate refresh token |

### Deliveries

| Method | Endpoint                         | Access               | Description                 |
| ------ | -------------------------------- | -------------------- | --------------------------- |
| POST   | `/api/deliveries/`               | Sender               | Create a new delivery       |
| GET    | `/api/deliveries/`               | Admin                | List all deliveries         |
| GET    | `/api/deliveries/{id}/`          | Sender, Rider, Admin | Get delivery detail         |
| PATCH  | `/api/deliveries/{id}/accept/`   | Rider                | Accept or reject assignment |
| PATCH  | `/api/deliveries/{id}/pickup/`   | Rider                | Mark package as picked up   |
| PATCH  | `/api/deliveries/{id}/transit/`  | Rider                | Mark as in transit          |
| PATCH  | `/api/deliveries/{id}/arrived/`  | Rider                | Trigger code generation     |
| POST   | `/api/deliveries/{id}/verify-a/` | Rider                | Submit Code A               |
| POST   | `/api/deliveries/{id}/verify-b/` | Customer             | Submit Code B               |

### Riders

| Method | Endpoint                     | Access | Description           |
| ------ | ---------------------------- | ------ | --------------------- |
| GET    | `/api/riders/`               | Admin  | List all riders       |
| GET    | `/api/riders/{id}/`          | Admin  | View rider profile    |
| PATCH  | `/api/riders/availability/`  | Rider  | Toggle online/offline |
| GET    | `/api/riders/me/deliveries/` | Rider  | View own deliveries   |

---

## Production Features

### Rate Limiting

- Login: 5 requests per minute per IP
- Delivery creation: 10 requests per hour per Sender
- State transitions: 20 requests per hour per Rider

### Caching (Redis)

- Rider availability list: 60 seconds, cleared on status change
- Delivery status reads: 30 seconds per delivery ID, cleared on state change
- Admin delivery list: 120 seconds per query

### Logging

Every state transition writes a structured log: delivery ID, actor ID, actor role, previous state, new state, timestamp. Complete audit trail on every delivery.

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/yourusername/flux.git
cd flux

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A flux worker --loglevel=info

# Start Celery Beat scheduler (separate terminal)
celery -A flux beat --loglevel=info
```

---
                                           |

## Live Demo

Coming Day 30.

API docs: `/api/docs/`

---

## Author

**Enoch Gbadebo (Datom)**
Backend Developer · Django / DRF / PostgreSQL

[LinkedIn](https://www.linkedin.com/in/gbadeboenoch/) · [GitHub](https://github.com/datom-code)

Built as part of #ENg30DayChallenge · #ENgShipIt
