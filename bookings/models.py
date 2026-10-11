from django.db import models
from django.contrib.auth.models import User
from trains.models import Train, Station, TrainClass
import random

class Coach(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='coaches')
    coach_code = models.CharField(max_length=10) # e.g. B1, B2, S1, S2, C1, H1
    travel_class = models.CharField(max_length=5, choices=TrainClass.CLASS_CHOICES)
    total_seats = models.PositiveIntegerField(default=72)

    class Meta:
        ordering = ['coach_code']
        unique_together = [('train', 'coach_code')]

    def __str__(self):
        return f"{self.train.train_number} - {self.coach_code} ({self.travel_class})"

class Seat(models.Model):
    BERTH_CHOICES = [
        ('LOWER', 'Lower Berth'),
        ('MIDDLE', 'Middle Berth'),
        ('UPPER', 'Upper Berth'),
        ('SIDE_LOWER', 'Side Lower'),
        ('SIDE_UPPER', 'Side Upper'),
        ('WINDOW', 'Window Seat'),
        ('AISLE', 'Aisle Seat'),
    ]

    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.PositiveIntegerField()
    berth_type = models.CharField(max_length=20, choices=BERTH_CHOICES, default='LOWER')

    class Meta:
        ordering = ['seat_number']
        unique_together = [('coach', 'seat_number')]

    def __str__(self):
        return f"{self.coach.coach_code}-{self.seat_number} ({self.berth_type})"

class JourneyInventory(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='inventories')
    journey_date = models.DateField(db_index=True)
    class_code = models.CharField(max_length=5, choices=TrainClass.CLASS_CHOICES)
    total_seats = models.PositiveIntegerField(default=72)
    booked_seats = models.PositiveIntegerField(default=0)
    available_seats = models.PositiveIntegerField(default=72)
    waitlist_count = models.PositiveIntegerField(default=0)
    max_waitlist = models.PositiveIntegerField(default=50)
    is_booking_open = models.BooleanField(default=True)

    class Meta:
        unique_together = [('train', 'journey_date', 'class_code')]
        indexes = [
            models.Index(fields=['train', 'journey_date', 'class_code']),
        ]

    def __str__(self):
        return f"{self.train.train_number} | {self.journey_date} | {self.class_code}: Avail {self.available_seats}, WL {self.waitlist_count}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('WAITLISTED', 'Waitlisted'),
        ('PARTIALLY_CANCELLED', 'Partially Cancelled'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed / Abandoned'),
    ]

    pnr = models.CharField(max_length=10, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='bookings')
    from_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='departing_bookings')
    to_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='arriving_bookings')
    journey_date = models.DateField(db_index=True)
    class_code = models.CharField(max_length=5)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    total_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PNR: {self.pnr} ({self.status}) - {self.train.train_number}"

    @property
    def confirmed_passengers_count(self):
        return self.passengers.filter(status='CONFIRMED').count()

    @property
    def waitlisted_passengers_count(self):
        return self.passengers.filter(status='WAITLISTED').count()

class Passenger(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('WAITLISTED', 'Waitlisted'),
        ('CANCELLED', 'Cancelled'),
    ]
    BERTH_PREF_CHOICES = [
        ('NONE', 'No Preference'),
        ('LOWER', 'Lower Berth'),
        ('MIDDLE', 'Middle Berth'),
        ('UPPER', 'Upper Berth'),
        ('SIDE_LOWER', 'Side Lower'),
        ('SIDE_UPPER', 'Side Upper'),
        ('WINDOW', 'Window Seat'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    berth_preference = models.CharField(max_length=20, choices=BERTH_PREF_CHOICES, default='NONE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    allocated_seat = models.ForeignKey(Seat, null=True, blank=True, on_delete=models.SET_NULL, related_name='passenger_allocations')
    waitlist_number = models.PositiveIntegerField(null=True, blank=True)
    fare = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        seat_str = f"Seat: {self.allocated_seat}" if self.allocated_seat else f"WL #{self.waitlist_number}"
        return f"{self.name} ({self.status} - {seat_str})"

class AllocatedJourneySeat(models.Model):
    """Physical concurrency lock record: one physical seat per journey date."""
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='journey_locks')
    journey_date = models.DateField(db_index=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='seat_lock')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='allocated_seats')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['seat', 'journey_date'], name='unique_seat_per_journey_date')
        ]

    def __str__(self):
        return f"{self.seat} on {self.journey_date}"

class WaitlistEntry(models.Model):
    """Queue entry for passengers on waitlist."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='waitlist_entries')
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE, related_name='waitlist_entry')
    inventory = models.ForeignKey(JourneyInventory, on_delete=models.CASCADE, related_name='waitlist_queue')
    position = models.PositiveIntegerField()
    is_promoted = models.BooleanField(default=False)
    promoted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"WL Position {self.position} - {self.passenger.name} ({self.inventory})"

class BookingLog(models.Model):
    """Audit trail of booking actions."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50) # 'CREATED', 'PAID', 'CONFIRMED', 'CANCELLED', etc.
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking.pnr} - {self.action} at {self.created_at}"
