from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state', 'id_proof_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'id_proof_number')
    list_filter = ('id_proof_type', 'state', 'created_at')

from .models import FavoriteRoute

@admin.register(FavoriteRoute)
class FavoriteRouteAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_station', 'to_station', 'created_at')

