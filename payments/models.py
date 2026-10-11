from django.db import models
from bookings.models import Booking
import uuid

class Payment(models.Model):
    METHOD_CHOICES = [
        ('DEMO_MOCK', 'Instant Educational Demo Simulator'),
        ('UPI', 'UPI / QR Code'),
        ('NET_BANKING', 'Internet Banking (Demo)'),
        ('DEBIT_CREDIT_CARD', 'Debit / Credit Card (Demo)'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('SUCCESS', 'Payment Successful'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=64, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='DEMO_MOCK')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    failure_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} ({self.status}) - ₹{self.amount}"

    @classmethod
    def generate_txn_id(cls):
        return f"TXN_DEMO_{uuid.uuid4().hex[:12].upper()}"
