from django.db import migrations
from django.core.management import call_command

def seed_railway_network(apps, schema_editor):
    try:
        call_command('seed_demo_data')
    except Exception as e:
        print(f"Notice: automatic seed_demo_data during migration encountered: {e}")

def reverse_seed(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('trains', '0001_initial'),
        ('bookings', '0002_cancellation'),
    ]

    operations = [
        migrations.RunPython(seed_railway_network, reverse_seed),
    ]
