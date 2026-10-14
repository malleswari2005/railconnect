from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('gateway/<str:pnr>/', views.demo_gateway_view, name='gateway'),
    path('failure/<str:pnr>/', views.payment_failure_view, name='failure'),
    path('retry/<str:pnr>/', views.retry_payment_view, name='retry'),
]
