from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from datetime import date, timedelta, time
from decimal import Decimal

from trains.models import Station, Train, TrainStop, TrainClass
from bookings.models import Booking, Passenger, JourneyInventory, Coach, Seat
from dashboard.models import (
    TTEAssignment, TicketCheck, TrainStatusUpdate, OperationalNotice, AuditLog
)
from dashboard.services import create_audit_log

class StaffPortalsTestCase(TestCase):
    """
    Comprehensive test suite covering role-based access control, cross-portal
    permission enforcement, TTE verification immutability, operations live sync,
    admin staff provisioning, password security, and audit logging.
    """
    def setUp(self):
        self.client = Client()

        # 1. Setup Role Groups
        self.groups = {}
        for role_name in ['Passenger', 'TTE', 'Operations', 'Admin']:
            grp, _ = Group.objects.get_or_create(name=role_name)
            self.groups[role_name] = grp

        # 2. Setup Test Users
        # Admin
        self.admin_user = User.objects.create_user(
            username='test_admin', password='AdminSecurePass@123', email='admin@test.local',
            is_staff=True, is_superuser=False
        )
        self.admin_user.groups.add(self.groups['Admin'])

        # TTE
        self.tte_user = User.objects.create_user(
            username='test_tte', password='TteSecurePass@123', email='tte@test.local',
            is_staff=False, is_superuser=False
        )
        self.tte_user.groups.add(self.groups['TTE'])

        # Operations
        self.ops_user = User.objects.create_user(
            username='test_ops', password='OpsSecurePass@123', email='ops@test.local',
            is_staff=False, is_superuser=False
        )
        self.ops_user.groups.add(self.groups['Operations'])

        # Passenger
        self.passenger_user = User.objects.create_user(
            username='test_passenger', password='PassSecure@123', email='pax@test.local',
            is_staff=False, is_superuser=False
        )
        self.passenger_user.groups.add(self.groups['Passenger'])

        # 3. Setup Test Stations & Trains
        self.st1 = Station.objects.create(code='BZA', name='Vijayawada Jn', city='Vijayawada', state='AP')
        self.st2 = Station.objects.create(code='VSKP', name='Visakhapatnam Jn', city='Visakhapatnam', state='AP')

        self.train1 = Train.objects.create(
            train_number='92801',
            name='Ratnachal Link Express',
            train_type='SUPERFAST',
            source_station=self.st1,
            destination_station=self.st2,
            departure_time=time(6, 0),
            arrival_time=time(12, 0),
            runs_on_days='MON,TUE,WED,THU,FRI,SAT,SUN',
            distance_km=350,
            is_active=True
        )

        self.train2 = Train.objects.create(
            train_number='92802',
            name='Simhadri Link Intercity',
            train_type='EXPRESS',
            source_station=self.st2,
            destination_station=self.st1,
            departure_time=time(14, 0),
            arrival_time=time(20, 0),
            runs_on_days='MON,TUE,WED,THU,FRI,SAT,SUN',
            distance_km=350,
            is_active=True
        )

        TrainStop.objects.create(train=self.train1, station=self.st1, stop_order=1, departure_time=time(6, 0))
        TrainStop.objects.create(train=self.train1, station=self.st2, stop_order=2, arrival_time=time(12, 0))

        # 4. Setup Test Booking & Passenger
        self.today = date.today()
        self.booking = Booking.objects.create(
            pnr='RC99887766',
            user=self.passenger_user,
            train=self.train1,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.today,
            class_code='3A',
            total_fare=Decimal('650.00'),
            status='CONFIRMED'
        )

        coach = Coach.objects.create(train=self.train1, coach_code='B1', travel_class='3A')
        seat = Seat.objects.create(coach=coach, seat_number=24, berth_type='LOWER')

        self.passenger = Passenger.objects.create(
            booking=self.booking,
            name='Kavitha Reddy',
            age=28,
            gender='F',
            status='CONFIRMED',
            allocated_seat=seat
        )

        # Assign TTE to Train 1 for today
        self.assignment = TTEAssignment.objects.create(
            tte=self.tte_user,
            train=self.train1,
            journey_date=self.today
        )

    # -------------------------------------------------------------
    # 1. Cross-Portal Permission Tests
    # -------------------------------------------------------------
    def test_guest_redirected_to_login(self):
        """Unauthenticated requests to any portal must redirect to login with ?next=."""
        for path in ['/tte/', '/operations/', '/admin-portal/']:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/accounts/login/', resp.url)
            self.assertIn(f'next={path}', resp.url)

    def test_passenger_forbidden_from_staff_portals(self):
        """Logged-in Passenger must be denied access with HTTP 403 to all new staff portals, and redirected from legacy staff dashboard."""
        self.client.force_login(self.passenger_user)
        for path in ['/tte/', '/operations/', '/admin-portal/']:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 403, f"Passenger should be forbidden from {path}")
            self.assertTemplateUsed(resp, '403.html')

        resp_legacy = self.client.get('/dashboard/staff/')
        self.assertEqual(resp_legacy.status_code, 302, "Passenger should be redirected from legacy staff dashboard")

    def test_tte_access_and_boundaries(self):
        """TTE can access /tte/ but is forbidden from /operations/ and /admin-portal/, and redirected from legacy staff dashboard."""
        self.client.force_login(self.tte_user)
        # Permitted
        resp_tte = self.client.get('/tte/')
        self.assertEqual(resp_tte.status_code, 200)

        # Forbidden with 403
        for path in ['/operations/', '/admin-portal/']:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 403, f"TTE should be forbidden from {path}")

        # Legacy staff dashboard requires is_staff (redirects)
        resp_legacy = self.client.get('/dashboard/staff/')
        self.assertEqual(resp_legacy.status_code, 302, "TTE without is_staff must not access legacy staff dashboard")

    def test_operations_access_and_boundaries(self):
        """Operations controller can access /operations/ but is forbidden from /tte/ and /admin-portal/, and redirected from legacy staff dashboard."""
        self.client.force_login(self.ops_user)
        # Permitted
        resp_ops = self.client.get('/operations/')
        self.assertEqual(resp_ops.status_code, 200)

        # Forbidden with 403
        for path in ['/tte/', '/admin-portal/']:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 403, f"Operations should be forbidden from {path}")

        # Legacy staff dashboard requires is_staff (redirects)
        resp_legacy = self.client.get('/dashboard/staff/')
        self.assertEqual(resp_legacy.status_code, 302, "Operations without is_staff must not access legacy staff dashboard")

    def test_admin_universal_access(self):
        """Admin has oversight access to /admin-portal/, /dashboard/staff/, /tte/, and /operations/."""
        self.client.force_login(self.admin_user)
        for path in ['/admin-portal/', '/dashboard/staff/', '/tte/', '/operations/']:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, f"Admin should have access to {path}")

    # -------------------------------------------------------------
    # 2. Role-Based Login Redirection Tests
    # -------------------------------------------------------------
    def test_role_based_login_redirection(self):
        """Verify login redirection by role tier with safe next handling."""
        # 1. Admin -> /admin-portal/
        resp_admin = self.client.post(reverse('accounts:login'), {
            'username': 'test_admin', 'password': 'AdminSecurePass@123'
        })
        self.assertRedirects(resp_admin, '/admin-portal/')
        self.client.logout()

        # 2. TTE -> /tte/
        resp_tte = self.client.post(reverse('accounts:login'), {
            'username': 'test_tte', 'password': 'TteSecurePass@123'
        })
        self.assertRedirects(resp_tte, '/tte/')
        self.client.logout()

        # 3. Operations -> /operations/
        resp_ops = self.client.post(reverse('accounts:login'), {
            'username': 'test_ops', 'password': 'OpsSecurePass@123'
        })
        self.assertRedirects(resp_ops, '/operations/')
        self.client.logout()

        # 4. Passenger -> core:home
        resp_pax = self.client.post(reverse('accounts:login'), {
            'username': 'test_passenger', 'password': 'PassSecure@123'
        })
        self.assertRedirects(resp_pax, reverse('core:home'))
        self.client.logout()

        # 5. Safe ?next is honored for any role
        resp_next = self.client.post(reverse('accounts:login') + '?next=/dashboard/my-bookings/', {
            'username': 'test_tte', 'password': 'TteSecurePass@123'
        })
        self.assertRedirects(resp_next, '/dashboard/my-bookings/')
        self.client.logout()

        # 6. Unsafe ?next is rejected and defaults to role home
        resp_unsafe = self.client.post(reverse('accounts:login') + '?next=https://malicious.example.com/', {
            'username': 'test_admin', 'password': 'AdminSecurePass@123'
        })
        self.assertRedirects(resp_unsafe, '/admin-portal/')

    # -------------------------------------------------------------
    # 3. TTE Verification & Immutability Tests
    # -------------------------------------------------------------
    def test_tte_passenger_verification_immutability(self):
        """
        CRITICAL REQUIREMENT: TTE verification must record TicketCheck
        WITHOUT EVER changing Passenger.status or Booking.status.
        """
        self.client.force_login(self.tte_user)

        # Check passenger
        resp = self.client.post(reverse('tte:tte_check_passenger'), {
            'assignment_id': self.assignment.id,
            'passenger_id': self.passenger.id,
            'result': 'VERIFIED',
            'remarks': 'Valid Aadhaar verified in seat'
        })
        self.assertRedirects(resp, reverse('tte:tte_chart', args=[self.assignment.id]))

        # Verify TicketCheck created
        ticket_check = TicketCheck.objects.filter(passenger=self.passenger, tte=self.tte_user).first()
        self.assertIsNotNone(ticket_check)
        self.assertEqual(ticket_check.result, 'VERIFIED')
        self.assertEqual(ticket_check.remarks, 'Valid Aadhaar verified in seat')

        # Strictly verify IMMUTABILITY of Booking & Passenger
        self.passenger.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.passenger.status, 'CONFIRMED', "Passenger status must remain CONFIRMED")
        self.assertEqual(self.booking.status, 'CONFIRMED', "Booking status must remain CONFIRMED")

    def test_tte_pnr_lookup_assignment_scope(self):
        """TTE PNR lookup allowed only for assigned journeys; unassigned returns error."""
        self.client.force_login(self.tte_user)

        # 1. Assigned journey lookup -> Success
        resp_assigned = self.client.get(reverse('tte:tte_pnr_lookup'), {'pnr': self.booking.pnr})
        self.assertEqual(resp_assigned.status_code, 200)
        self.assertContains(resp_assigned, 'Kavitha Reddy')
        self.assertContains(resp_assigned, 'RC99887766')

        # 2. Create another booking on unassigned Train 2
        unassigned_booking = Booking.objects.create(
            pnr='RC11223344',
            user=self.passenger_user,
            train=self.train2,
            from_station=self.st2,
            to_station=self.st1,
            journey_date=self.today,
            class_code='SL',
            total_fare=Decimal('250.00'),
            status='CONFIRMED'
        )

        resp_unassigned = self.client.get(reverse('tte:tte_pnr_lookup'), {'pnr': unassigned_booking.pnr})
        self.assertEqual(resp_unassigned.status_code, 200)
        self.assertContains(resp_unassigned, "Journey not assigned to you.")
        # Ensure booking manifest details are hidden
        self.assertIsNone(resp_unassigned.context['booking'])
        self.assertNotContains(resp_unassigned, "Passenger List")
        self.assertNotContains(resp_unassigned, "Simhadri Link Intercity")

    # -------------------------------------------------------------
    # 4. Operations Live-Status Sync Tests
    # -------------------------------------------------------------
    def test_operations_status_update_syncs_to_public_live_status(self):
        """
        Public /trains/live-status/ displays sample label when no update exists,
        and switches to Live Operations Feed when an update is broadcasted.
        """
        # 1. Initial public query with no live update posted today
        resp_initial = self.client.get(reverse('trains:live_status'), {'train_number': self.train1.train_number})
        self.assertEqual(resp_initial.status_code, 200)
        self.assertTrue(resp_initial.context['is_sample'])
        self.assertContains(resp_initial, "Sample data (no live update posted today)")

        # 2. Operations posts an update
        self.client.force_login(self.ops_user)
        post_resp = self.client.post(reverse('operations:ops_update_status'), {
            'train_id': self.train1.id,
            'journey_date': self.today.strftime('%Y-%m-%d'),
            'current_station_id': self.st1.id,
            'status': 'DELAYED',
            'delay_minutes': 25,
            'remarks': 'Signal clearance delay at Krishna Canal'
        })
        self.assertRedirects(post_resp, reverse('operations:ops_dashboard'))

        # 3. Public query again -> Now reads real update
        self.client.logout()
        resp_updated = self.client.get(reverse('trains:live_status'), {'train_number': self.train1.train_number})
        self.assertEqual(resp_updated.status_code, 200)
        self.assertFalse(resp_updated.context['is_sample'])
        self.assertEqual(resp_updated.context['data_source'], "Live Operations Control Feed")
        self.assertContains(resp_updated, "Live Operations Control Feed")
        self.assertContains(resp_updated, "25m delay")
        self.assertContains(resp_updated, "Signal clearance delay at Krishna Canal")

    # -------------------------------------------------------------
    # 5. Admin Staff Provisioning & Password Validation Tests
    # -------------------------------------------------------------
    def test_admin_staff_creation_security_and_password_validation(self):
        """
        Admin creating staff accounts must enforce validate_password,
        create users with is_staff=False and is_superuser=False, and assign proper Group.
        """
        self.client.force_login(self.admin_user)

        # 1. Weak password rejected
        weak_resp = self.client.post(reverse('admin_portal:admin_create_staff'), {
            'username': 'new_staff_weak',
            'email': 'weak@test.local',
            'role': 'TTE',
            'password': '123',
            'confirm_password': '123'
        })
        self.assertEqual(weak_resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='new_staff_weak').exists(), "Weak password user should not be created")
        self.assertContains(weak_resp, "Password security issue")

        # 2. Valid staff creation -> TTE
        valid_resp = self.client.post(reverse('admin_portal:admin_create_staff'), {
            'username': 'new_tte_user',
            'email': 'tte_new@test.local',
            'first_name': 'Ramesh',
            'last_name': 'Babu',
            'phone_number': '9848012345',
            'role': 'TTE',
            'password': 'ComplexStaffPass@2026',
            'confirm_password': 'ComplexStaffPass@2026'
        })
        self.assertRedirects(valid_resp, reverse('admin_portal:admin_users'))

        created_tte = User.objects.get(username='new_tte_user')
        self.assertFalse(created_tte.is_staff, "TTE user must NOT be is_staff")
        self.assertFalse(created_tte.is_superuser, "TTE user must NOT be is_superuser")
        self.assertTrue(created_tte.groups.filter(name='TTE').exists())

    def test_admin_tte_assignment_management(self):
        """Admin can assign TTE to train and date, and revoke assignments."""
        self.client.force_login(self.admin_user)

        tomorrow = self.today + timedelta(days=1)
        # Create assignment
        assign_resp = self.client.post(reverse('admin_portal:admin_assignments'), {
            'tte_id': self.tte_user.id,
            'train_id': self.train2.id,
            'journey_date': tomorrow.strftime('%Y-%m-%d')
        })
        self.assertRedirects(assign_resp, reverse('admin_portal:admin_assignments'))

        new_assignment = TTEAssignment.objects.filter(
            tte=self.tte_user, train=self.train2, journey_date=tomorrow
        ).first()
        self.assertIsNotNone(new_assignment)

        # Revoke / Delete assignment
        del_resp = self.client.post(reverse('admin_portal:admin_delete_assignment', args=[new_assignment.id]))
        self.assertRedirects(del_resp, reverse('admin_portal:admin_assignments'))
        self.assertFalse(TTEAssignment.objects.filter(id=new_assignment.id).exists())

    # -------------------------------------------------------------
    # 6. Audit Logging Verification
    # -------------------------------------------------------------
    def test_immutable_audit_logging(self):
        """Staff actions create audit log records accessible in the admin audit trail."""
        self.client.force_login(self.admin_user)

        # Trigger audit log
        log = create_audit_log(
            actor=self.admin_user,
            action='TEST_ADMIN_ACTION',
            object_repr='Test Target Object',
            details='Validation of audit log subsystem'
        )
        self.assertIsNotNone(log)

        # Query audit logs view
        audit_resp = self.client.get(reverse('admin_portal:admin_audit_logs'))
        self.assertEqual(audit_resp.status_code, 200)
        self.assertContains(audit_resp, 'TEST_ADMIN_ACTION')
        self.assertContains(audit_resp, 'Test Target Object')
