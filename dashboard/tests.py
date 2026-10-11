from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta, time
from decimal import Decimal
from trains.models import Station, Train, TrainStop, TrainClass
from bookings.models import Booking, Passenger, JourneyInventory, Cancellation
from bookings.services import (
    get_or_create_inventory,
    allocate_booking_seats_atomic,
    cancel_booking_or_passengers
)

class DashboardAndCancellationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='traveller1', password='Pass@123')
        self.client.login(username='traveller1', password='Pass@123')

        self.st1 = Station.objects.create(code='NDLS', name='New Delhi', city='Delhi', state='Delhi')
        self.st2 = Station.objects.create(code='CNB', name='Kanpur Central', city='Kanpur', state='UP')

        self.train = Train.objects.create(
            train_number='12004',
            name='Lucknow Shatabdi',
            train_type='SHATABDI',
            source_station=self.st1,
            destination_station=self.st2,
            departure_time=time(6, 10),
            arrival_time=time(11, 20),
            distance_km=436,
            runs_on_days='MON,TUE,WED,THU,FRI,SAT,SUN'
        )

        TrainStop.objects.create(train=self.train, station=self.st1, stop_order=1, departure_time=time(6, 10))
        TrainStop.objects.create(train=self.train, station=self.st2, stop_order=2, arrival_time=time(11, 20), distance_from_source_km=436)

        TrainClass.objects.create(
            train=self.train,
            class_code='CC',
            class_name='AC Chair Car',
            base_fare=Decimal('300.00'),
            per_km_rate=Decimal('1.00'),
            total_coaches=1,
            seats_per_coach=1 # Exactly 1 seat capacity!
        )

        self.journey_date = date.today() + timedelta(days=5) # >48 hours in future
        inv = get_or_create_inventory(self.train, self.journey_date, 'CC')
        inv.total_seats = 1
        inv.available_seats = 1
        inv.save()

    def test_cancellation_refund_and_auto_waitlist_promotion(self):
        # 1. Booking A takes the only available seat (Confirmed)
        b_a = Booking.objects.create(
            pnr='1111111111',
            user=self.user,
            train=self.train,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.journey_date,
            class_code='CC',
            status='CONFIRMED',
            total_fare=Decimal('1000.00')
        )
        p_a = Passenger.objects.create(booking=b_a, name='Passenger A', age=30, gender='M', fare=Decimal('1000.00'))
        allocate_booking_seats_atomic(b_a)
        p_a.refresh_from_db()
        self.assertEqual(p_a.status, 'CONFIRMED')
        allocated_seat = p_a.allocated_seat
        self.assertIsNotNone(allocated_seat)

        # 2. Booking B arrives when capacity is 0 (Waitlisted)
        user_b = User.objects.create_user(username='waitlisted_user', password='Pass@123')
        b_b = Booking.objects.create(
            pnr='2222222222',
            user=user_b,
            train=self.train,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.journey_date,
            class_code='CC',
            status='PENDING',
            total_fare=Decimal('1000.00')
        )
        p_b = Passenger.objects.create(booking=b_b, name='Passenger B', age=25, gender='F', fare=Decimal('1000.00'))
        allocate_booking_seats_atomic(b_b)
        b_b.refresh_from_db()
        p_b.refresh_from_db()
        self.assertEqual(b_b.status, 'WAITLISTED')
        self.assertEqual(p_b.status, 'WAITLISTED')
        self.assertEqual(p_b.waitlist_number, 1)

        # 3. Passenger A cancels booking (>48h before departure = 90% refund)
        cancellation = cancel_booking_or_passengers(b_a, reason='Test plan change')
        self.assertIsNotNone(cancellation)
        self.assertEqual(cancellation.refund_amount, Decimal('900.00')) # 90% of 1000
        self.assertEqual(cancellation.cancellation_fee, Decimal('100.00')) # 10% clerkage

        b_a.refresh_from_db()
        self.assertEqual(b_a.status, 'CANCELLED')

        # 4. Check that Passenger B was automatically promoted!
        p_b.refresh_from_db()
        b_b.refresh_from_db()
        self.assertEqual(p_b.status, 'CONFIRMED')
        self.assertEqual(p_b.allocated_seat, allocated_seat)
        self.assertEqual(b_b.status, 'CONFIRMED')
