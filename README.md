# 🚆 RailConnect – Smart Railway Reservation System

[![Django](https://img.shields.io/badge/Django-6.0-092e20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-51%20Passed%20(100%25)-success.svg)](#-automated-testing)
[![Offline](https://img.shields.io/badge/Offline-100%25%20Self--Contained-orange.svg)](#-offline-readiness)

An enterprise-grade Django web application inspired by the **Indian Railway Catering and Tourism Corporation (IRCTC)** reservation architecture, featuring a realistic **Andhra Pradesh-focused railway network** (40+ stations, 39 fictional trains, 7 trunk/intercity corridors) and **Three Role-Based Staff Portals** (TTE Duty Portal, Operations Control Room, and Administrator Control Tower). Built to demonstrate high-concurrency seat locking, database normalization, automated waitlist promotion, and offline resilience.

> **Notice on Timetables & Train Data**:
> Train numbers (fictional 9xxxx series), train names, halt timings, fare calculations, and seat availability represented in this project are sample data generated for demonstration purposes and are **not** real Indian Railways or IRCTC schedules.

---

## 🏛️ Role-Based Staff Portals & Architecture

RailConnect provides role-based access control (RBAC) enforced via server-side Django Groups and role decorators with custom 403 Forbidden pages and intelligent role-based login redirection:

1. **Traveling Ticket Examiner (TTE) Portal (`/tte/`)**:
   - **Duty Dashboard**: Live assigned train services for today, upcoming duty schedules, and past services.
   - **Reservation Charts**: Coach-wise passenger manifests with verification status filtering (Verified, Absent, Irregular, Invalid ID).
   - **Ticket Verification**: Records immutable `TicketCheck` inspection events. Under strict security protocol, TTE verification **never** mutates core `Passenger.status` or `Booking.status`.
   - **Duty PNR Lookup**: Restricted strictly to the TTE's explicitly assigned journeys.

2. **Operations Control Center (`/operations/`)**:
   - **Fleet Status Monitor**: Real-time operational overview of running trains, delays, and current station locations.
   - **Live Dispatch Broadcasts**: Posts real-time train status updates (`TrainStatusUpdate`) that immediately sync with the public passenger-facing `/trains/live-status/` tracker.
   - **Network Operational Bulletins**: Publish, manage, and archive operational alerts and speed/platform notices (`OperationalNotice`).
   - **Dispatch Audit Trail**: Historical search of all operational broadcasts by train number and journey date.

3. **Administrator Control Tower (`/admin-portal/`)**:
   - **User & Staff Directory**: Complete user directory with role tier inspection and staff account provisioning (TTE & Operations only, with strict Django password validation enforcement). TTE and Operations accounts do not receive administrative `is_staff` or superuser privileges.
   - **TTE Duty Rosters**: Schedule, assign, and revoke TTE duty assignments to trains and journey dates.
   - **System-Wide Reservations Search**: Comprehensive reservation search by PNR, passenger name, route, and date with refund tracking.
   - **Simulated Payment Ledger**: Audit simulated payment gateway transactions, gateway reference IDs, and payment methods.
   - **Operational Intelligence & Reports**: Class-wise revenue breakdown, top train volume, and waitlist fulfillment conversion metrics.
   - **Immutable System Audit Trail**: Complete activity audit trail capturing staff creations, TTE assignments, status broadcasts, and ticket checks.

---

## 🌟 Core System Features

1. **High-Concurrency Seat Engine**:
   - Pessimistic row-level locking via `select_for_update()` inside `transaction.atomic()` blocks.
   - Physical database constraint `UniqueConstraint(fields=['seat', 'journey_date'])` strictly preventing double-bookings.
2. **Intermediate Stations & Route Search**:
   - Multi-stop train schedules with arrival/departure timings, halt durations, and distance calculations.
   - Chronological route traversal verifying $Stop_{from} < Stop_{to}$ and day-of-week operation.
3. **Automated FIFO Waitlist Engine**:
   - Automatic promotion of earliest waitlisted passenger to confirmed upon seat cancellation with zero manual intervention.
   - Real-time queue position renumbering.
4. **Transparent Tiered Cancellation & Refund Matrix**:
   - `> 48 hours`: **90% refund** (10% clerkage charge retained).
   - `12 to 48 hours`: **50% refund**.
   - `< 12 hours`: **0% refund** (Non-refundable).
5. **Interactive Demo Payment Gateway**:
   - Explicitly labeled educational simulation with toggleable **Success** and **Failure** outcomes to test transactional rollbacks.
6. **Digital E-Tickets & Vector PDF Generation**:
   - Downloadable Electronic Reservation Slip (ERS) rendered as high-fidelity vector PDF using **ReportLab**.
   - On-the-fly scannable QR verification code.
7. **Control Room Staff Dashboard**:
   - Operational KPIs: Total Revenue, Active Trains, Confirmed vs Waitlisted vs Cancelled.
   - Local offline **Chart.js** telemetry for status and travel class distributions.
8. **100% Offline Resilience**:
   - Local vendor packaging of Bootstrap 5.3 CSS/JS and Chart.js inside `static/vendor/`—zero external CDN dependencies.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  Responsive HTML5 / CSS3 / Vanilla JS + Bootstrap 5.3 (Offline Local Bundle)      |
|  Navy Blue (#0B1F3A), Pure White (#FFFFFF), Vibrant Orange (#FF7A18) Accent       |
+-----------------------------------------------------------------------------------+
                                        |  HTTP/HTTPS Requests (CSRF Protected)
+---------------------------------------v-------------------------------------------+
|                                DJANGO 6 APP CORE                                  |
|  +--------------------+  +--------------------+  +--------------------+           |
|  |     accounts       |  |       trains       |  |      bookings      |           |
|  | Auth, RBAC Groups, |  | Stations, Routes,  |  | Inventory, Seats,  |           |
|  | Role Redirection   |  | Search & Live Feed |  | Concurrency Engine |           |
|  +--------------------+  +--------------------+  +--------------------+           |
|  +--------------------+  +--------------------+  +--------------------+           |
|  |     payments       |  |     dashboard      |  |       core         |           |
|  | Demo Gateway,      |  | TTE, Operations,   |  | Shared Base UI,    |           |
|  | Ledger Records     |  | Admin, Audit Trail |  | Error Handlers 403 |           |
|  +--------------------+  +--------------------+  +--------------------+           |
+-----------------------------------------------------------------------------------+
       |                                   |                           |
+------v-----------+             +---------v---------+       +---------v---------+
| SQLite (Dev)     |             | ReportLab Engine  |       | QRCode + Pillow   |
| PostgreSQL (Prod)|             | Vector PDF Slip   |       | Safe Verification |
+------------------+             +-------------------+       +-------------------+
```

---

## ⚡ Quick Start & Installation

### Prerequisites
- Python 3.12+ / 3.14
- Git

### 1. Clone & Enter Project Directory
```bash
git clone <repository-url>
cd railconnect
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Realistic Demo Data
```bash
python manage.py migrate
python manage.py seed_demo_data
```
> `seed_demo_data` automatically seeds:
> - 43 Andhra Pradesh network stations and national trunk anchors (BZA, VSKP, TPTY, RU, GNT, NLR, SBC, MAS, SC, etc.)
> - 39 Realistic train services with physical coaches, seats, and 14-day inventories
> - 4 Role-based Groups (`Passenger`, `TTE`, `Operations`, `Admin`)
> - 5 Pre-configured demo accounts

### 5. Launch the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 👥 Demo Accounts & Credentials

| Role | Username | Password (Default) | Environment Variable Override | Purpose & Access Level |
| :--- | :--- | :--- | :--- | :--- |
| **System Admin** | `staff_admin` | `AdminPass@123` | `ADMIN_DEMO_PASSWORD` | Universal oversight, `/admin-portal/`, staff provisioning, `/admin/` |
| **TTE Officer** | `tte_officer` | `TtePass@123` | `TTE_DEMO_PASSWORD` | Access to `/tte/`, duty charts, passenger verification, duty PNR lookup |
| **Operations Controller** | `ops_controller` | `OpsPass@123` | `OPS_DEMO_PASSWORD` | Access to `/operations/`, status broadcasts, alerts, dispatch history |
| **Passenger 1** | `passenger1` | `Pass@123` | &mdash; | Pre-configured customer with existing bookings and journey history |
| **Passenger 2** | `passenger2` | `Pass@123` | &mdash; | Second customer for testing waitlist promotion & concurrent bookings |

> [!IMPORTANT]
> **Production & Render Deployment Security Note**:
> Demo staff passwords can be overridden by setting the environment variables `ADMIN_DEMO_PASSWORD`, `TTE_DEMO_PASSWORD`, and `OPS_DEMO_PASSWORD`. In production environments (such as Render or Railway), these environment variables **must be configured** with strong passwords to secure staff portals.

---

## 🧪 Automated Testing

RailConnect comes with a comprehensive test suite of **51 automated tests** covering authentication, search validation, concurrency locks, double booking prevention, tiered cancellations, waitlist FIFO shifts, cross-portal role permission enforcement, TTE verification immutability, operations live sync, password security, and AP network stop chronology:

```bash
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
...................................................
----------------------------------------------------------------------
Ran 51 tests in ~115s

OK
Destroying test database for alias 'default'...
```

---

## 🚀 Production Deployment (Render / Railway / Heroku)

1. Set environment variables in your hosting dashboard:
   ```env
   SECRET_KEY=<strong-random-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=<your-domain>.render.com,localhost
   DATABASE_URL=postgres://user:password@host:port/dbname
   ADMIN_DEMO_PASSWORD=<strong-admin-password>
   TTE_DEMO_PASSWORD=<strong-tte-password>
   OPS_DEMO_PASSWORD=<strong-ops-password>
   ```
2. Build command:
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py seed_demo_data && python manage.py collectstatic --noinput
   ```
3. Start command (configured in `Procfile`):
   ```bash
   web: gunicorn railconnect.wsgi --log-file -
   ```

---

## 📜 License & Notice
This project is open-source under the MIT License and was developed for professional demonstration and evaluation purposes.
