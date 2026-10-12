# 🚆 RailConnect – Smart Railway Reservation System

[![Django](https://img.shields.io/badge/Django-6.0-092e20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-30%20Passed%20(100%25)-success.svg)](#-automated-testing)
[![Offline](https://img.shields.io/badge/Offline-100%25%20Self--Contained-orange.svg)](#-offline-readiness)

An enterprise-grade Django web application inspired by the **Indian Railway Catering and Tourism Corporation (IRCTC)** reservation architecture, featuring a realistic **Andhra Pradesh-focused railway network** (30+ stations, 36 fictional trains, 7 trunk/intercity corridors). Built to demonstrate high-concurrency seat locking, database normalization, automated waitlist promotion, and offline resilience.

> **Notice on Timetables & Train Data**:
> Train numbers (fictional 9xxxx series), train names, halt timings, fare calculations, and seat availability represented in this project are sample data generated for demonstration purposes and are **not** real Indian Railways or IRCTC schedules.

---

## 🌟 Key Features

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
|  Navy Blue (#0b2545), Pure White (#ffffff), Vibrant Orange (#ff7a00) Accent       |
+-----------------------------------------------------------------------------------+
                                        |  HTTP/HTTPS Requests (CSRF Protected)
+---------------------------------------v-------------------------------------------+
|                                DJANGO 6 APP CORE                                  |
|  +--------------------+  +--------------------+  +--------------------+           |
|  |     accounts       |  |       trains       |  |      bookings      |           |
|  | Auth, Profiles,    |  | Stations, Routes,  |  | Inventory, Seats,  |           |
|  | Ownership Guards   |  | Search & Schedules |  | Concurrency Engine |           |
|  +--------------------+  +--------------------+  +--------------------+           |
|  +--------------------+  +--------------------+  +--------------------+           |
|  |     payments       |  |     dashboard      |  |       core         |           |
|  | Demo Gateway,      |  | Staff Analytics,   |  | Shared Base UI,    |           |
|  | State Transitions  |  | Customer Portal    |  | Error Handlers     |           |
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
> - 15 Major Indian Railway Stations (NDLS, MMCT, HWH, SBC, MAS, ADI, CNB, PNBE, etc.)
> - 12 Multi-stop Trains with Classes & Berths (Rajdhani, Shatabdi, Vande Bharat, etc.)
> - 3 Pre-configured Demo Accounts for instant evaluation

### 5. Launch the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 👥 Demo Accounts & Credentials (Viva Ready)

| Role | Username | Password | Purpose & Access Level |
| :--- | :--- | :--- | :--- |
| **Control Room Admin** | `staff_admin` | `AdminPass@123` | Full access to Staff Dashboard, KPIs, charts, train master, and `/admin/` |
| **Passenger 1** | `passenger1` | `Pass@123` | Pre-configured customer with existing bookings and journey history |
| **Passenger 2** | `passenger2` | `Pass@123` | Second customer for testing waitlist promotion & concurrent bookings |

---

## 🧪 Automated Testing

RailConnect comes with a comprehensive test suite of **30 automated tests** covering authentication, search validation, concurrency locks, double booking prevention, tiered cancellations, waitlist FIFO shifts, staff access controls, and AP network stop chronology, distance monotonicity, tariff calculation, and search validation:

```bash
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
..............................
----------------------------------------------------------------------
Ran 30 tests in ~35s

OK
Destroying test database for alias 'default'...
```

---

## 📖 Step-by-Step Viva Demonstration Walkthrough

1. **Search Trains**:
   - On the homepage, select **From: NDLS** and **To: CNB** with a future date.
   - Click **Find Trains**. Observe multi-stop trains passing through Kanpur Central with class-wise fare calculation.
2. **Book Tickets**:
   - Click **Book** on AC 3-Tier (3A). Enter passenger names and berth preferences.
   - Review booking summary on the review screen.
3. **Simulate Payment**:
   - On the Demo Payment Gateway, click **Simulate Successful Payment**.
   - Notice atomic seat reservation and automatic redirection to the Digital Boarding Pass with scannable QR.
4. **Download PDF Ticket**:
   - Click **Download Vector PDF** to inspect the ReportLab ERS slip.
5. **Verify Waitlist Auto-Promotion**:
   - Log in as `passenger2`. Book the remaining seat until waitlisted.
   - Switch back to `passenger1` and cancel the confirmed seat from **My Bookings**.
   - Notice that `passenger1` receives a calculated 90% refund and `passenger2` is automatically promoted to Confirmed!
6. **Inspect Staff Dashboard**:
   - Log in as `staff_admin` and navigate to **Staff Dashboard**.
   - View real-time revenue telemetry and interactive Chart.js graphs.

---

## 📚 Technical Documentation

Detailed architectural and viva reference documents are located in `docs/`:
- **[PROJECT_SPEC.md](docs/PROJECT_SPEC.md)**: Full functional & non-functional technical specification.
- **[ER_DIAGRAM.md](docs/ER_DIAGRAM.md)**: Mermaid Entity-Relationship diagram and normalization analysis.
- **[CANCELLATION_AND_WAITLIST_RULES.md](docs/CANCELLATION_AND_WAITLIST_RULES.md)**: Detailed refund tier formulas and waitlist promotion state diagrams.
- **[TEAM_PLAN.md](docs/TEAM_PLAN.md)**: 5-member team module division, code contracts, and student viva question guide.

---

## 🚀 Production Deployment (Render / Railway / Heroku)

1. Set environment variables in your hosting dashboard:
   ```env
   SECRET_KEY=<strong-random-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=<your-domain>.render.com,localhost
   DATABASE_URL=postgres://user:password@host:port/dbname
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

## 📜 License & Academic Notice
This project is open-source under the MIT License and was developed for educational and academic evaluation purposes.
