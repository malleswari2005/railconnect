"""
WSGI config for railconnect project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'railconnect.settings')

application = get_wsgi_application()

# Production database safeguard: ensure stations and trains are seeded on deployment startup
try:
    from django.db import connection
    if 'trains_station' in connection.introspection.table_names():
        from trains.models import Station
        if Station.objects.count() == 0:
            from django.core.management import call_command
            call_command('seed_demo_data')
except Exception:
    pass

