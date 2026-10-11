from django.contrib import admin
from .models import Coach, Seat, JourneyInventory, Booking, Passenger, AllocatedJourneySeat, WaitlistEntry, BookingLog, Cancellation

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0

class BookingLogInline(admin.TabularInline):
    model = BookingLog
    extra = 0
    readonly_fields = ('action', 'description', 'created_at')

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('train', 'coach_code', 'travel_class', 'total_seats')
    list_filter = ('travel_class', 'train')
    inlines = [SeatInline]

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('coach', 'seat_number', 'berth_type')
    list_filter = ('berth_type', 'coach__travel_class')
    search_fields = ('coach__coach_code', 'seat_number')

@admin.register(JourneyInventory)
class JourneyInventoryAdmin(admin.ModelAdmin):
    list_display = ('train', 'journey_date', 'class_code', 'total_seats', 'available_seats', 'booked_seats', 'waitlist_count', 'is_booking_open')
    list_filter = ('class_code', 'journey_date', 'train')
    search_fields = ('train__train_number', 'train__name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'user', 'train', 'journey_date', 'class_code', 'status', 'total_fare', 'created_at')
    list_filter = ('status', 'class_code', 'journey_date')
    search_fields = ('pnr', 'user__username', 'contact_phone', 'contact_email')
    inlines = [PassengerInline, BookingLogInline]

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'booking', 'status', 'allocated_seat', 'waitlist_number', 'fare')
    list_filter = ('status', 'gender')
    search_fields = ('name', 'booking__pnr')

@admin.register(AllocatedJourneySeat)
class AllocatedJourneySeatAdmin(admin.ModelAdmin):
    list_display = ('seat', 'journey_date', 'passenger', 'booking', 'created_at')
    list_filter = ('journey_date',)
    search_fields = ('seat__coach__coach_code', 'booking__pnr')

@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'passenger', 'inventory', 'position', 'is_promoted', 'promoted_at')
    list_filter = ('is_promoted', 'inventory__class_code')

@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ('booking', 'cancelled_passengers_count', 'refund_amount', 'cancellation_fee', 'created_at')
    list_filter = ('refund_status', 'created_at')
    search_fields = ('booking__pnr',)

@admin.register(BookingLog)
class BookingLogAdmin(admin.ModelAdmin):
    list_display = ('booking', 'action', 'created_at')
    list_filter = ('action',)
    search_fields = ('booking__pnr', 'description')
