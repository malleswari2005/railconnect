from django.db import migrations

def setup_roles_and_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')

    roles = ['Passenger', 'TTE', 'Operations', 'Admin']
    groups = {}
    for role in roles:
        group, _ = Group.objects.get_or_create(name=role)
        groups[role] = group

    for user in User.objects.all():
        if user.is_superuser or user.is_staff or user.username == 'staff_admin':
            user.groups.add(groups['Admin'])
        else:
            if not user.groups.exists():
                user.groups.add(groups['Passenger'])

def reverse_roles_and_groups(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_favoriteroute'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(setup_roles_and_groups, reverse_roles_and_groups),
    ]
