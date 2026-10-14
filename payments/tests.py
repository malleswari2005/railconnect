from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta, time
from trains.models import Station, Train, TrainStop, TrainClass
from bookings.models import Booking, Passenger, JourneyInventory
from bookings.services import get_or_create_inventory
from payments.models import Payment

class PaymentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='payuser', password='Pass@123')
        self.client.login(username='payuser', password='Pass@123')

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
            seats_per_coach=10
        )

        self.journey_date = date.today() + timedelta(days=7)
        get_or_create_inventory(self.train, self.journey_date, 'CC')

        self.booking = Booking.objects.create(
            pnr='9876543210',
            user=self.user,
            train=self.train,
            from_station=self.st1,
            to_station=self.st2,
            journey_date=self.journey_date,
            class_code='CC',
            status='PENDING',
            total_fare=Decimal('811.00'),
            contact_email='payuser@example.com',
            contact_phone='9876543210'
        )
        self.passenger = Passenger.objects.create(
            booking=self.booking,
            name='Rohan',
            age=26,
            gender='M',
            fare=Decimal('811.00')
        )

    def test_payment_success_flow(self):
        """Test payment success simulation: confirms booking and allocates seat."""
        response = self.client.post(reverse('payments:gateway', args=[self.booking.pnr]), {
            'outcome': 'SUCCESS',
            'payment_method': 'UPI'
        })
        self.assertEqual(response.status_code, 302)
        
        self.booking.refresh_from_db()
        self.passenger.refresh_from_db()
        self.assertEqual(self.booking.status, 'CONFIRMED')
        self.assertEqual(self.passenger.status, 'CONFIRMED')
        self.assertIsNotNone(self.passenger.allocated_seat)

        payment = Payment.objects.filter(booking=self.booking).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'SUCCESS')
        self.assertEqual(payment.amount, Decimal('811.00'))

    def test_payment_failure_flow(self):
        """Test payment failure simulation: leaves booking in failed state."""
        response = self.client.post(reverse('payments:gateway', args=[self.booking.pnr]), {
            'outcome': 'FAILURE',
            'payment_method': 'DEBIT_CREDIT_CARD',
            'failure_reason': 'Card Declined'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payments:failure', args=[self.booking.pnr]))

        self.booking.refresh_from_db()
        self.passenger.refresh_from_db()
        self.assertEqual(self.booking.status, 'FAILED')
        self.assertIsNone(self.passenger.allocated_seat)

        payment = Payment.objects.filter(booking=self.booking).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'FAILED')
