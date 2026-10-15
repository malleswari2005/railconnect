from django.urls import path
from . import views_tte

app_name = 'tte'

urlpatterns = [
    path('', views_tte.tte_dashboard_view, name='tte_dashboard'),
    path('chart/<int:assignment_id>/', views_tte.tte_reservation_chart_view, name='tte_chart'),
    path('check-passenger/', views_tte.tte_check_passenger_view, name='tte_check_passenger'),
    path('pnr-lookup/', views_tte.tte_pnr_lookup_view, name='tte_pnr_lookup'),
]
