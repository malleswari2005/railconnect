from django.urls import path
from . import views_ops

app_name = 'operations'

urlpatterns = [
    path('', views_ops.ops_dashboard_view, name='ops_dashboard'),
    path('update-status/', views_ops.ops_update_status_view, name='ops_update_status'),
    path('history/', views_ops.ops_history_view, name='ops_history'),
    path('notice/create/', views_ops.ops_create_notice_view, name='ops_create_notice'),
    path('notice/<int:notice_id>/toggle/', views_ops.ops_toggle_notice_view, name='ops_toggle_notice'),
]
