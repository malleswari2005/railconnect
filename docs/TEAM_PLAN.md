# RailConnect – 5-Member Team Project Plan & Viva Guide

## 1. Team Structure & Module Ownership Overview

This document allocates responsibilities across a 5-member MCA project group. Each member has distinct file ownership and a clear narrative for viva examination.

```
+-----------------------------------------------------------------------------------------+
|                                    TEAM LEAD & SYSTEM ARCHITECT                         |
|                                        (Member 1 / Member 4)                            |
+-----------------------------------------------------------------------------------------+
       |                           |                          |                          |
+------v--------------+  +---------v------------+  +----------v-----------+  +-----------v------------+
| Member 1            |  | Member 2             |  | Member 3             |  | Member 4 / Member 5    |
| UI/UX & Base Layout |  | Auth & Security      |  | Trains & Schedules   |  | Bookings, Payments, QA |
+---------------------+  +----------------------+  +----------------------+  +------------------------+
```

---

## 2. Individual Member Work Breakdown

### 👤 Member 1: UI/UX Architect & Base Frontend Specialist
- **Assigned Module**: `core` app, Design System & Static Vendor Bundles
- **Code Ownership**:
  - `templates/base.html`, `templates/partials/*`, `templates/core/*`
  - `static/css/custom.css`, `static/js/main.js`
  - `templates/404.html`, `templates/500.html`
  - `core/views.py`, `core/context_processors.py`
- **Key Deliverables**:
  - Offline local packaging of Bootstrap 5.3 and custom IRCTC-inspired navy/orange visual theme.
  - Branded responsive layout, mobile collapse navbar, auto-dismissing flash messages.
  - Global context processor exposing system flags across all views.
- **Viva Defense Questions & Answers**:
  - *Q: Why bundle Bootstrap and Chart.js locally instead of using CDNs?*  
    *A: College viva presentations frequently lack internet connectivity. Storing vendor bundles in `static/vendor/` guarantees 100% offline uptime.*
  - *Q: How does `core.context_processors.global_context` work?*  
    *A: It automatically injects project variables (`PROJECT_NAME`, `DEMO_REFUND_POLICY`, `CURRENT_YEAR`) into every template render context without manual view passing.*

---

### 👤 Member 2: Authentication & User Profile Security Engineer
- **Assigned Module**: `accounts` app & Ownership Controls
- **Code Ownership**:
  - `accounts/models.py` (`Profile`, `FavoriteRoute`)
  - `accounts/forms.py` (Validation rules, passwords, profile updates)
  - `accounts/views.py` (Registration, login, logout, profile view)
  - `accounts/tests.py`
- **Key Deliverables**:
  - 1-to-1 extension of Django `User` with identity proofs (Aadhaar, PAN, Passport).
  - Post-save Django signals for automatic profile generation.
  - Strict ownership validation preventing unauthorized profile edits.
- **Viva Defense Questions & Answers**:
  - *Q: How do you prevent users from accessing or editing other users' profiles?*  
    *A: Views use `@login_required` and explicitly query `request.user.profile` rather than accepting arbitrary user IDs in the request body or URL parameters.*
  - *Q: Why use post_save signals for the Profile model?*  
    *A: Signals decouple user account creation from profile initialization, ensuring every user (via registration form, admin panel, or fixtures) automatically has an associated profile record.*

---

### 👤 Member 3: Railway Network & Schedules Engine Specialist
- **Assigned Module**: `trains` app & Search Algorithms
- **Code Ownership**:
  - `trains/models.py` (`Station`, `Train`, `TrainStop`, `TrainClass`)
  - `trains/views.py` (`train_search_view`, `train_schedule_view`, `live_status_view`)
  - `trains/management/commands/seed_demo_data.py`
  - `trains/tests.py`
- **Key Deliverables**:
  - Database schema for multi-stop train routes and intermediate station halts.
  - Intermediate route search algorithm verifying chronological stop sequence ($Stop_{from} < Stop_{to}$).
  - Simulated live train running status visualization.
  - Automated seeding of 15 realistic stations and 12 multi-class trains.
- **Viva Defense Questions & Answers**:
  - *Q: How does the search algorithm handle intermediate stations?*  
    *A: It queries all active trains running on the day of week. For each train, it retrieves stops matching origin and destination. A train is valid if both stops exist and the boarding stop order is less than the deboarding stop order.*
  - *Q: How is day of week filtering handled?*  
    *A: The journey date is converted to an uppercase day abbreviation (`journey_date.strftime('%a').upper()`), which is matched against the train's `runs_on_days` comma-separated list.*

---

### 👤 Member 4: Concurrency & Booking Transaction Engine Engineer
- **Assigned Module**: `bookings` app & PDF Engine
- **Code Ownership**:
  - `bookings/models.py` (`Coach`, `Seat`, `JourneyInventory`, `Booking`, `Passenger`, `AllocatedJourneySeat`)
  - `bookings/services.py` (Fare calculation, atomic seat allocation, PNR generation)
  - `bookings/views.py` (Booking flow, sanitized PNR lookup, ReportLab PDF ticket generation)
  - `bookings/tests.py`
- **Key Deliverables**:
  - Concurrency-safe atomic seat allocation using `select_for_update()` inside `transaction.atomic()`.
  - Database `UniqueConstraint(fields=['seat', 'journey_date'])` preventing double booking.
  - Vector PDF ticket generation via ReportLab with scannable QR verification code.
  - Privacy-preserving public PNR inquiry view.
- **Viva Defense Questions & Answers**:
  - *Q: How do you prevent double-booking during concurrent user requests?*  
    *A: By combining row-level database locking (`select_for_update()`) inside an atomic transaction with a database-level unique constraint on `(seat_id, journey_date)`. This physically forbids two transactions from claiming the same seat.*
  - *Q: Why generate PDF tickets on the fly with ReportLab instead of client-side HTML-to-PDF?*  
    *A: Server-side vector generation ensures uniform PDF layout across all browsers and devices without depending on browser print drivers or client-side JavaScript.*

---

### 👤 Member 5: Payment Gateway Simulation, Analytics & QA Lead
- **Assigned Module**: `payments`, `dashboard` & Test Suite
- **Code Ownership**:
  - `payments/models.py` (`Payment`) & `payments/views.py` (Demo Gateway state machine)
  - `dashboard/views.py` (`staff_dashboard_view`, `my_bookings_view`, `cancel_booking_view`)
  - `bookings/services.py` (`promote_waitlist_on_seat_release`, `cancel_booking_or_passengers`)
  - `dashboard/tests.py`, `payments/tests.py`
- **Key Deliverables**:
  - Interactive demo payment gateway with explicit success and failure simulation.
  - Tiered refund policy implementation (>48h: 90%, 12-48h: 50%, <12h: 0%).
  - Automated FIFO waitlist promotion engine upon ticket cancellation.
  - Staff operational analytics dashboard with local Chart.js visual telemetry.
  - Comprehensive automated test suite with 20+ unit tests across all applications.
- **Viva Defense Questions & Answers**:
  - *Q: What happens when a confirmed passenger cancels their seat?*  
    *A: The cancellation service calculates the tiered refund based on hours until departure. It deletes the physical seat lock and calls `promote_waitlist_on_seat_release()`, which automatically allocates the released berth to the first waitlisted passenger and shifts remaining queue positions forward.*
  - *Q: How does the staff dashboard ensure security?*  
    *A: Access is restricted using `@user_passes_test(lambda u: u.is_staff)`. Regular users trying to access staff endpoints are redirected to the login page.*

---

## 3. Git Collaboration & Integration Protocol
1. **Branching Strategy**:
   - `main`: Production-ready, verified codebase.
   - `feature/<module>`: Feature branches worked on by individual members.
2. **Commit Policy**:
   - Every commit must contain clear descriptive messages formatted as `Phase X: <module> - <features>`.
   - All tests (`python manage.py test`) must pass with 0 failures before merging into `main`.
