# RailConnect – Project Specification & System Architecture

## 1. Project Title & Overview
**RailConnect: Smart Railway Reservation & Passenger Fleet Management System**  
An enterprise-grade, high-concurrency educational web application designed for MCA capstone evaluation. It demonstrates production-level Django software engineering modeled after Indian Railway reservation standards (IRCTC).

---

## 2. Problem Statement & Academic Motivation
Traditional academic reservation projects often suffer from:
1. **Double Booking Flaws**: Relying on simple database queries (`available_seats > 0`) without pessimistic row locks allows concurrent transactions to book the exact same berth.
2. **Monolithic Spaghetti Code**: Lack of separation between authentication, inventory, fare calculation, and reporting.
3. **External Dependencies**: Breaking during offline college viva presentations due to CDN script outages.
4. **Simplistic Cancellation**: Ignoring real-world ticket cancellation time-windows and waitlist queue shifts.

RailConnect directly solves these challenges through:
- **Pessimistic Row Locking**: Enforcing `select_for_update()` inside `transaction.atomic()` blocks.
- **Physical Seat Constraints**: `UniqueConstraint(fields=['seat', 'journey_date'])` guaranteeing absolute zero double-bookings.
- **Rule-Based FIFO Waitlist Engine**: Automatic queue advancement upon berth cancellation.
- **100% Offline Capability**: All Bootstrap 5.3 and Chart.js bundles stored locally in `static/vendor/`.

---

## 3. Technology Stack Specification
- **Framework**: Django 6.x
- **Language**: Python 3.14 / 3.12+
- **Database Engine**:
  - Development: SQLite 3
  - Production: PostgreSQL (auto-configured via `dj-database-url` and `psycopg-binary`)
- **Static Assets Serving**: WhiteNoise 6.6 with manifest caching
- **Frontend Architecture**:
  - Responsive HTML5 & CSS3 with Bootstrap 5.3 (Offline bundle)
  - Color Scheme: Navy Blue (`#0b2545`), Clean White, Vibrant Orange (`#ff7a00`)
  - Dynamic Client UI: Vanilla ES6 JS (No heavy framework required for presentation viva)
  - Data Visualizations: Chart.js 4.4 UMD (Offline local bundle)
- **Document Generation**: ReportLab 5.x for vector Electronic Reservation Slips (ERS)
- **Security & QR**: `qrcode` + `Pillow` generating on-the-fly verification codes

---

## 4. Application Module Breakdown

| Django App | Domain Scope | Key Models & Services |
| :--- | :--- | :--- |
| **`core`** | System foundation | Base layouts, navigation, error handlers (404/500), context processors |
| **`accounts`** | User management & Identity | `Profile`, `FavoriteRoute`, forms, authentication, ownership checks |
| **`trains`** | Railway network | `Station`, `Train`, `TrainStop`, `TrainClass`, timetable, live simulator |
| **`bookings`** | Transactional engine | `Coach`, `Seat`, `JourneyInventory`, `Booking`, `Passenger`, `AllocatedJourneySeat`, `WaitlistEntry`, `Cancellation`, `BookingLog` |
| **`payments`** | Financial simulation | `Payment` state machine, success/failure simulator, audit logger |
| **`dashboard`** | Analytics & Oversight | Customer "My Bookings" portal, staff KPI telemetry, Chart.js visuals |

---

## 5. Security & Ownership Architecture
- **CSRF Protection**: Universal CSRF tokens enforced on all POST endpoints.
- **Pessimistic DB Locks**: Prevents race conditions during simultaneous booking requests.
- **Access Guards**:
  - `@login_required` on passenger booking and profile operations.
  - `@user_passes_test(lambda u: u.is_staff)` on control room dashboards.
  - Strict ownership validation ensuring passengers cannot view or cancel other users' bookings.
- **Sanitized Public Inquiries**: PNR status lookup strips all phone numbers, email addresses, and identification proofs.

---

## 6. End-to-End Operational Lifecycle
1. **Search**: Passenger queries Origin &rarr; Destination on a specific date. Multi-stop route algorithm locates trains passing both stops in chronological sequence.
2. **Passenger Entry**: Formset accepts 1 to 6 passengers with berth preferences.
3. **Draft Booking**: System creates Pending Booking with unique 10-digit numeric PNR.
4. **Payment Simulation**: User selects simulated payment method (UPI, Card, Net Banking) and triggers outcome.
5. **Atomic Allocation**: On success, `select_for_update()` allocates physical berths or waitlist queue positions atomically.
6. **Ticket Generation**: System renders digital boarding pass with scannable QR verification code and ReportLab PDF download.
7. **Cancellation**: If cancelled, tiered refund (90% / 50% / 0%) is calculated, seats are released, and waitlist auto-promotion triggers automatically.
