from django.urls import path
from . import views

app_name = 'trains'

urlpatterns = [
    path('search/', views.train_search_view, name='search'),
    path('schedule/<str:train_number>/', views.train_schedule_view, name='schedule'),
    path('live-status/', views.live_status_view, name='live_status'),
    path('api/stations/', views.station_autocomplete_view, name='api_stations'),
]
