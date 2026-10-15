from django.urls import path
from . import views_admin

app_name = 'admin_portal'

urlpatterns = [
    path('', views_admin.admin_dashboard_view, name='admin_dashboard'),
    path('users/', views_admin.admin_users_view, name='admin_users'),
    path('users/create/', views_admin.admin_create_staff_view, name='admin_create_staff'),
    path('assignments/', views_admin.admin_assignments_view, name='admin_assignments'),
    path('assignments/<int:assignment_id>/delete/', views_admin.admin_delete_assignment_view, name='admin_delete_assignment'),
    path('bookings/', views_admin.admin_bookings_view, name='admin_bookings'),
    path('payments/', views_admin.admin_payments_view, name='admin_payments'),
    path('reports/', views_admin.admin_reports_view, name='admin_reports'),
    path('audit-logs/', views_admin.admin_audit_logs_view, name='admin_audit_logs'),
]
