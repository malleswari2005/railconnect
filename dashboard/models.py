from django.db import models
from django.contrib.auth.models import User
from trains.models import Train, Station
from bookings.models import Booking, Passenger

class TTEAssignment(models.Model):
    """
    Assigns a TTE (Traveling Ticket Examiner) to a specific train and journey date.
    """
    tte = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tte_assignments')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='tte_assignments')
    journey_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tte', 'train', 'journey_date')
        ordering = ['-journey_date', 'train']

    def __str__(self):
        return f"{self.tte.username} - {self.train.number} ({self.journey_date})"


class TicketCheck(models.Model):
    """
    Immutable record of a ticket verification performed by a TTE on a passenger.
    Note: A TicketCheck NEVER mutates the passenger's or booking's status.
    """
    CHECK_RESULTS = [
        ('VERIFIED', 'Verified / Present'),
        ('ABSENT', 'Passenger Absent / No-Show'),
        ('IRREGULAR', 'Irregular / Penalty Due'),
        ('WRONG_ID', 'Invalid Identity Document'),
    ]

    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='ticket_checks')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='ticket_checks')
    tte = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_checks_performed')
    checked_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, choices=CHECK_RESULTS, default='VERIFIED')
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        return f"Check {self.passenger.name} ({self.booking.pnr}) - {self.result} by {self.tte.username}"


class TrainStatusUpdate(models.Model):
    """
    Real-time operational status updates posted by Operations controllers.
    """
    STATUS_CHOICES = [
        ('ON_TIME', 'On Time'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
        ('DIVERTED', 'Diverted'),
        ('RESCHEDULED', 'Rescheduled'),
    ]

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='status_updates')
    journey_date = models.DateField()
    current_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='train_status_updates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ON_TIME')
    delay_minutes = models.PositiveIntegerField(default=0)
    expected_arrival = models.TimeField(null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ops_train_updates')
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.train.number} on {self.journey_date}: {self.get_status_display()} ({self.delay_minutes}m)"


class OperationalNotice(models.Model):
    """
    System-wide or internal operational notices posted by Operations/Admin.
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High / Urgent'),
        ('CRITICAL', 'Critical Alert'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    is_active = models.BooleanField(default=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ops_notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.priority}] {self.title}"


class AuditLog(models.Model):
    """
    Immutable audit log capturing staff activities across TTE, Operations, and Admin portals.
    """
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.actor}: {self.action} on {self.object_repr}"
