from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ID_PROOF_CHOICES = [
        ('AADHAAR', 'Aadhaar Card'),
        ('PAN', 'PAN Card'),
        ('PASSPORT', 'Passport'),
        ('VOTER_ID', 'Voter ID Card'),
        ('DRIVING_LICENSE', 'Driving License'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES, default='AADHAAR')
    id_proof_number = models.CharField(max_length=30, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

class FavoriteRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_routes')
    from_station = models.ForeignKey('trains.Station', on_delete=models.CASCADE, related_name='+')
    to_station = models.ForeignKey('trains.Station', on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'from_station', 'to_station')]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.from_station.code} -> {self.to_station.code}"

