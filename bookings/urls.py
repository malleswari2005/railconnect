from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('new/', views.booking_new_view, name='new'),
    path('review/<str:pnr>/', views.booking_review_view, name='review'),
    path('pnr-lookup/', views.pnr_lookup_view, name='pnr_lookup'),
    path('ticket/<str:pnr>/', views.ticket_detail_view, name='ticket_detail'),
    path('ticket/<str:pnr>/pdf/', views.ticket_pdf_view, name='ticket_pdf'),
]
