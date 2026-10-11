from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import date, timedelta, time
from decimal import Decimal
from trains.models import Station, Train, TrainStop, TrainClass
from bookings.models import Coach, Seat, JourneyInventory, Booking, Passenger, AllocatedJourneySeat, WaitlistEntry
from bookings.services import (
    generate_unique_pnr,
    calculate_fare,
    get_or_create_inventory,
    allocate_booking_seats_atomic,
    promote_waitlist_on_seat_release,
)

class BookingsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testbooker', password='Pass@123')
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

        TrainStop.objects.create(train=self.train, station=self.st1, stop_order=1, departure_time=time(6, 10), distance_from_source_km=0)
        TrainStop.objects.create(train=self.train, station=self.st2, stop_order=2, arrival_time=time(11, 20), distance_from_source_km=436)

        TrainClass.objects.create(
            train=self.train,
            class_code='CC',
            class_name='AC Chair Car',
            base_fare=Decimal('300.00'),
            per_km_rate=Decimal('1.00'),
            total_coaches=1,
            seats_per_coach=2 # Tiny capacity for easy test overflow
        )

        self.journey_date = date.today() + timedelta(days=7)

    def test_pnr_generation(self):
        pnr = generate_unique_pnr()
        self.assertEqual(len(pnr), 10)
        self.assertTrue(pnr.isdigit())

    def test_fare_calculation(self):
        fare, dist = calculate_fare(self.train, 'CC', self.st1, self.st2)
        # Distance = 436. Base 300 + 436*1.0 + 75 (Shatabdi surcharge) = 811.00
        self.assertEqual(fare, Decimal('811.00'))
        self.assertEqual(dist, 436)

    def test_atomic_seat_allocation_and_waitlist(self):
        # Initial inventory capacity is 2 seats
        inv = get_or_create_inventory(self.train, self.journey_date, 'CC')
        inv.total_seats = 2
        inv.available_seats = 2
        inv.save()

        # Booking 1: 2 passengers (should be CONFIRMED)
        b1 = Booking.objects.create(
            pnr='1111111111',
            user=self.user,
            train=self.train,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.journey_date,
            class_code='CC',
            status='PENDING',
            total_fare=Decimal('1622.00')
        )
        p1 = Passenger.objects.create(booking=b1, name='Alice', age=25, gender='F')
        p2 = Passenger.objects.create(booking=b1, name='Bob', age=30, gender='M')

        allocate_booking_seats_atomic(b1)
        b1.refresh_from_db()
        p1.refresh_from_db()
        p2.refresh_from_db()
        inv.refresh_from_db()

        self.assertEqual(b1.status, 'CONFIRMED')
        self.assertEqual(p1.status, 'CONFIRMED')
        self.assertIsNotNone(p1.allocated_seat)
        self.assertEqual(p2.status, 'CONFIRMED')
        self.assertIsNotNone(p2.allocated_seat)
        self.assertNotEqual(p1.allocated_seat, p2.allocated_seat)
        self.assertEqual(inv.available_seats, 0)

        # Booking 2: 1 passenger (capacity exhausted, should be WAITLISTED)
        b2 = Booking.objects.create(
            pnr='2222222222',
            user=self.user,
            train=self.train,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.journey_date,
            class_code='CC',
            status='PENDING',
            total_fare=Decimal('811.00')
        )
        p3 = Passenger.objects.create(booking=b2, name='Charlie', age=35, gender='M')

        allocate_booking_seats_atomic(b2)
        b2.refresh_from_db()
        p3.refresh_from_db()
        inv.refresh_from_db()

        self.assertEqual(b2.status, 'WAITLISTED')
        self.assertEqual(p3.status, 'WAITLISTED')
        self.assertIsNone(p3.allocated_seat)
        self.assertEqual(p3.waitlist_number, 1)
        self.assertEqual(inv.waitlist_count, 1)

    def test_double_booking_database_constraint(self):
        """Verifies database-level impossibility of double-booking same seat on same date."""
        inv = get_or_create_inventory(self.train, self.journey_date, 'CC')
        coach = Coach.objects.filter(train=self.train, travel_class='CC').first()
        seat = coach.seats.first()

        b = Booking.objects.create(
            pnr='3333333333',
            user=self.user,
            train=self.train,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.journey_date,
            class_code='CC'
        )
        p1 = Passenger.objects.create(booking=b, name='P1', age=20, gender='M')
        p2 = Passenger.objects.create(booking=b, name='P2', age=22, gender='F')

        AllocatedJourneySeat.objects.create(seat=seat, journey_date=self.journey_date, passenger=p1, booking=b)
        
        # Second allocation of the exact same seat on same date must raise IntegrityError!
        with self.assertRaises(IntegrityError):
            AllocatedJourneySeat.objects.create(seat=seat, journey_date=self.journey_date, passenger=p2, booking=b)
