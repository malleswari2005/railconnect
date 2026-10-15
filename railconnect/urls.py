from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('trains/', include('trains.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('tte/', include('dashboard.urls_tte')),
    path('operations/', include('dashboard.urls_ops')),
    path('admin-portal/', include('dashboard.urls_admin')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'core.views.handler403_view'
handler404 = 'core.views.handler404_view'
handler500 = 'core.views.handler500_view'
