from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel/<str:pnr>/', views.cancel_booking_view, name='cancel_booking'),
    path('staff/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/trains/', views.staff_trains_view, name='staff_trains'),
    path('staff/bookings/', views.staff_bookings_view, name='staff_bookings'),
]
