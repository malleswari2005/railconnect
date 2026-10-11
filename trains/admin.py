from django.contrib import admin
from .models import Station, Train, TrainStop, TrainClass

class TrainStopInline(admin.TabularInline):
    model = TrainStop
    extra = 1

class TrainClassInline(admin.TabularInline):
    model = TrainClass
    extra = 1

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'state', 'zone')
    search_fields = ('code', 'name', 'city')
    list_filter = ('zone', 'state')

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'name', 'train_type', 'source_station', 'destination_station', 'departure_time', 'arrival_time', 'is_active')
    search_fields = ('train_number', 'name')
    list_filter = ('train_type', 'is_active')
    inlines = [TrainStopInline, TrainClassInline]

@admin.register(TrainStop)
class TrainStopAdmin(admin.ModelAdmin):
    list_display = ('train', 'stop_order', 'station', 'arrival_time', 'departure_time', 'distance_from_source_km')
    list_filter = ('train',)
    search_fields = ('train__train_number', 'station__name', 'station__code')

@admin.register(TrainClass)
class TrainClassAdmin(admin.ModelAdmin):
    list_display = ('train', 'class_code', 'class_name', 'base_fare', 'per_km_rate', 'total_coaches', 'seats_per_coach')
    list_filter = ('class_code',)
