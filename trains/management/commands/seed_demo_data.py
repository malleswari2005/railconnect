import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from datetime import time, date, timedelta
from trains.models import Station, Train, TrainStop, TrainClass
from bookings.models import Coach, Seat, JourneyInventory
from bookings.services import get_or_create_coaches_and_seats
from trains.data.ap_railway_data import STATIONS_DATA, TRAINS_DATA

class Command(BaseCommand):
    help = 'Idempotently seeds realistic AP railway network: stations, 36 trains, stops, tariffs, coaches, and 14-day inventory'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting RailConnect Andhra Pradesh network seeding..."))

        # -------------------------------------------------------------
        # 1. Setup Roles & Seed Accounts (Admin, TTE, Operations, Passenger)
        # -------------------------------------------------------------
        groups = {}
        for role_name in ['Passenger', 'TTE', 'Operations', 'Admin']:
            grp, _ = Group.objects.get_or_create(name=role_name)
            groups[role_name] = grp

        admin_pwd = os.environ.get('ADMIN_DEMO_PASSWORD', 'AdminPass@123')
        tte_pwd = os.environ.get('TTE_DEMO_PASSWORD', 'TtePass@123')
        ops_pwd = os.environ.get('OPS_DEMO_PASSWORD', 'OpsPass@123')

        # Admin: staff_admin (Only Admin & superusers get is_staff)
        admin_user, created = User.objects.get_or_create(
            username='staff_admin',
            defaults={
                'email': 'staff@railconnect.local',
                'first_name': 'Chief',
                'last_name': 'Controller',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password(admin_pwd)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_user.groups.add(groups['Admin'])
        if hasattr(admin_user, 'profile'):
            admin_user.profile.phone_number = '9810011223'
            admin_user.profile.city = 'Vijayawada'
            admin_user.profile.save()

        # TTE Officer: tte_officer (Not is_staff)
        tte_user, created = User.objects.get_or_create(
            username='tte_officer',
            defaults={
                'email': 'tte@railconnect.local',
                'first_name': 'Suresh',
                'last_name': 'Kumar',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        tte_user.set_password(tte_pwd)
        tte_user.is_staff = False
        tte_user.is_superuser = False
        tte_user.save()
        tte_user.groups.add(groups['TTE'])
        if hasattr(tte_user, 'profile'):
            tte_user.profile.phone_number = '9811223344'
            tte_user.profile.city = 'Vijayawada'
            tte_user.profile.save()

        # Operations Controller: ops_controller (Not is_staff)
        ops_user, created = User.objects.get_or_create(
            username='ops_controller',
            defaults={
                'email': 'ops@railconnect.local',
                'first_name': 'Ramesh',
                'last_name': 'Chandra',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        ops_user.set_password(ops_pwd)
        ops_user.is_staff = False
        ops_user.is_superuser = False
        ops_user.save()
        ops_user.groups.add(groups['Operations'])
        if hasattr(ops_user, 'profile'):
            ops_user.profile.phone_number = '9822334455'
            ops_user.profile.city = 'Guntur'
            ops_user.profile.save()

        # Passenger 1
        p1, created = User.objects.get_or_create(
            username='passenger1',
            defaults={
                'email': 'passenger1@example.com',
                'first_name': 'Aarav',
                'last_name': 'Sharma',
                'is_staff': False,
            }
        )
        p1.set_password('Pass@123')
        p1.is_staff = False
        p1.save()
        p1.groups.add(groups['Passenger'])
        if hasattr(p1, 'profile'):
            p1.profile.phone_number = '9876543210'
            p1.profile.city = 'Visakhapatnam'
            p1.profile.save()

        # Passenger 2
        p2, created = User.objects.get_or_create(
            username='passenger2',
            defaults={
                'email': 'passenger2@example.com',
                'first_name': 'Priya',
                'last_name': 'Nair',
                'is_staff': False,
            }
        )
        p2.set_password('Pass@123')
        p2.is_staff = False
        p2.save()
        p2.groups.add(groups['Passenger'])
        if hasattr(p2, 'profile'):
            p2.profile.phone_number = '9876501234'
            p2.profile.city = 'Tirupati'
            p2.profile.save()

        # Ensure all existing and newly found users belong to at least one group
        for u in User.objects.all():
            if not u.groups.exists():
                if u.is_superuser or u.is_staff or u.username == 'staff_admin':
                    u.groups.add(groups['Admin'])
                else:
                    u.groups.add(groups['Passenger'])

        self.stdout.write(self.style.SUCCESS("Verified accounts & roles: staff_admin, tte_officer, ops_controller, passenger1, passenger2"))

        # -------------------------------------------------------------
        # 2. Seed Stations (Idempotent update_or_create)
        # -------------------------------------------------------------
        station_objs = {}
        for code, name, city, state, zone in STATIONS_DATA:
            st, _ = Station.objects.update_or_create(
                code=code,
                defaults={'name': name, 'city': city, 'state': state, 'zone': zone}
            )
            station_objs[code] = st

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(station_objs)} stations (AP network & national anchors)."))

        # -------------------------------------------------------------
        # 3. Seed Preserved National Trains for Test Compatibility
        # -------------------------------------------------------------
        national_trains_data = [
            {
                'number': '12301',
                'name': 'Howrah Rajdhani Express',
                'type': 'RAJDHANI',
                'src': 'HWH', 'dest': 'NDLS',
                'dep': time(16, 50), 'arr': time(10, 5),
                'dist': 1450,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('HWH', 1, None, time(16, 50), 0, 0, 0),
                    ('PNBE', 2, time(22, 10), time(22, 20), 10, 532, 0),
                    ('CNB', 3, time(4, 45), time(4, 55), 10, 1014, 1),
                    ('NDLS', 4, time(10, 5), None, 0, 1450, 1),
                ],
                'classes': [
                    ('1A', 'AC First Class', 2200, 2.50, 1, 24),
                    ('2A', 'AC 2-Tier', 1400, 1.80, 2, 48),
                    ('3A', 'AC 3-Tier', 950, 1.25, 4, 64),
                ]
            },
            {
                'number': '12302',
                'name': 'Kolkata Rajdhani Express',
                'type': 'RAJDHANI',
                'src': 'NDLS', 'dest': 'HWH',
                'dep': time(16, 55), 'arr': time(9, 55),
                'dist': 1450,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('NDLS', 1, None, time(16, 55), 0, 0, 0),
                    ('CNB', 2, time(21, 30), time(21, 40), 10, 436, 0),
                    ('PNBE', 3, time(3, 40), time(3, 50), 10, 918, 1),
                    ('HWH', 4, time(9, 55), None, 0, 1450, 1),
                ],
                'classes': [
                    ('1A', 'AC First Class', 2200, 2.50, 1, 24),
                    ('2A', 'AC 2-Tier', 1400, 1.80, 2, 48),
                    ('3A', 'AC 3-Tier', 950, 1.25, 4, 64),
                ]
            },
            {
                'number': '12004',
                'name': 'Lucknow Shatabdi',
                'type': 'SHATABDI',
                'src': 'NDLS', 'dest': 'CNB',
                'dep': time(6, 10), 'arr': time(11, 20),
                'dist': 436,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('NDLS', 1, None, time(6, 10), 0, 0, 0),
                    ('CNB', 2, time(11, 20), None, 0, 436, 0),
                ],
                'classes': [
                    ('CC', 'AC Chair Car', 300, 1.00, 4, 78),
                    ('1A', 'Executive Chair Car', 700, 1.80, 1, 46),
                ]
            },
        ]

        # Combine AP Network Trains + National compatibility trains
        all_trains = list(TRAINS_DATA) + national_trains_data

        # -------------------------------------------------------------
        # 4. Seed Trains, Stops, and Classes (Idempotent)
        # -------------------------------------------------------------
        self.stdout.write(self.style.NOTICE(f"Seeding {len(all_trains)} trains and stops..."))

        seeded_train_objs = []
        for tdata in all_trains:
            train, _ = Train.objects.update_or_create(
                train_number=tdata['number'],
                defaults={
                    'name': tdata['name'],
                    'train_type': tdata['type'],
                    'source_station': station_objs[tdata['src']],
                    'destination_station': station_objs[tdata['dest']],
                    'departure_time': tdata['dep'],
                    'arrival_time': tdata['arr'],
                    'distance_km': tdata['dist'],
                    'runs_on_days': tdata['days'],
                    'is_active': True,
                }
            )
            seeded_train_objs.append(train)

            # Stops: Idempotently sync stops
            TrainStop.objects.filter(train=train).delete()
            stops_to_create = []
            for st_code, order, arr, dep, halt, dist, offset in tdata['stops']:
                stops_to_create.append(TrainStop(
                    train=train,
                    station=station_objs[st_code],
                    stop_order=order,
                    arrival_time=arr,
                    departure_time=dep,
                    halt_minutes=halt,
                    distance_from_source_km=dist,
                    day_offset=offset,
                ))
            TrainStop.objects.bulk_create(stops_to_create)

            # Classes: Idempotently sync classes
            TrainClass.objects.filter(train=train).delete()
            classes_to_create = []
            for c_code, c_name, base, per_km, coaches, seats in tdata['classes']:
                classes_to_create.append(TrainClass(
                    train=train,
                    class_code=c_code,
                    class_name=c_name,
                    base_fare=base,
                    per_km_rate=per_km,
                    total_coaches=coaches,
                    seats_per_coach=seats,
                ))
            TrainClass.objects.bulk_create(classes_to_create)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(all_trains)} trains with stops and coach classes."))

        # -------------------------------------------------------------
        # 5. Generate Physical Coaches & Seats
        # -------------------------------------------------------------
        self.stdout.write(self.style.NOTICE("Ensuring physical coaches and seats exist..."))
        for train in seeded_train_objs:
            for tc in train.classes.all():
                get_or_create_coaches_and_seats(train, tc.class_code)

        # -------------------------------------------------------------
        # 6. Generate 14-Day Upfront Journey Inventory (bulk_create)
        # -------------------------------------------------------------
        self.stdout.write(self.style.NOTICE("Generating upfront Journey Inventory for the next 14 days..."))
        today = date.today()
        target_dates = [today + timedelta(days=d) for d in range(14)]

        # Find existing inventories to prevent duplicates
        existing_keys = set(
            JourneyInventory.objects.filter(
                journey_date__gte=today,
                journey_date__lte=today + timedelta(days=14)
            ).values_list('train_id', 'journey_date', 'class_code')
        )

        inventory_to_create = []
        for train in seeded_train_objs:
            for dt in target_dates:
                day_abbr = dt.strftime('%a').upper()
                if not train.runs_on_day(day_abbr):
                    continue

                for tc in train.classes.all():
                    key = (train.id, dt, tc.class_code)
                    if key in existing_keys:
                        continue

                    total_cap = tc.total_seats
                    inventory_to_create.append(JourneyInventory(
                        train=train,
                        journey_date=dt,
                        class_code=tc.class_code,
                        total_seats=total_cap,
                        booked_seats=0,
                        available_seats=total_cap,
                        waitlist_count=0,
                        max_waitlist=50,
                        is_booking_open=True,
                    ))
                    existing_keys.add(key)

        if inventory_to_create:
            JourneyInventory.objects.bulk_create(inventory_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Created {len(inventory_to_create)} new inventory records."))
        else:
            self.stdout.write(self.style.SUCCESS("All 14-day inventories already exist."))

        # -------------------------------------------------------------
        # 7. Print Statistics Summary
        # -------------------------------------------------------------
        station_count = Station.objects.count()
        train_count = Train.objects.count()
        coach_count = Coach.objects.count()
        seat_count = Seat.objects.count()
        inventory_count = JourneyInventory.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f"\n[NETWORK SEEDING COMPLETE]\n"
            f"- Stations: {station_count}\n"
            f"- Trains: {train_count}\n"
            f"- Coaches: {coach_count}\n"
            f"- Seats: {seat_count}\n"
            f"- Journey Inventories: {inventory_count}\n"
        ))
