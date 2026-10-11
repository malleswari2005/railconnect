from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import time, date, timedelta
from trains.models import Station, Train, TrainStop, TrainClass
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Seeds realistic educational demo data: users, 15+ stations, 12+ trains with stops and classes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting RailConnect demo data seeding..."))

        # 1. Seed Demo Accounts
        # Staff Admin
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
        if created:
            admin_user.set_password('AdminPass@123')
            admin_user.save()
            admin_user.profile.phone_number = '9810011223'
            admin_user.profile.city = 'New Delhi'
            admin_user.profile.save()
            self.stdout.write(self.style.SUCCESS("Created staff_admin (AdminPass@123)"))
        else:
            admin_user.set_password('AdminPass@123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        # Demo Passenger 1
        p1, created = User.objects.get_or_create(
            username='passenger1',
            defaults={
                'email': 'passenger1@example.com',
                'first_name': 'Aarav',
                'last_name': 'Sharma',
            }
        )
        if created:
            p1.set_password('Pass@123')
            p1.save()
            p1.profile.phone_number = '9876543210'
            p1.profile.city = 'Mumbai'
            p1.profile.save()
            self.stdout.write(self.style.SUCCESS("Created passenger1 (Pass@123)"))

        # Demo Passenger 2
        p2, created = User.objects.get_or_create(
            username='passenger2',
            defaults={
                'email': 'passenger2@example.com',
                'first_name': 'Priya',
                'last_name': 'Nair',
            }
        )
        if created:
            p2.set_password('Pass@123')
            p2.save()
            p2.profile.phone_number = '9876501234'
            p2.profile.city = 'Bengaluru'
            p2.profile.save()
            self.stdout.write(self.style.SUCCESS("Created passenger2 (Pass@123)"))

        # 2. Seed 15 Major Stations
        stations_data = [
            ('NDLS', 'New Delhi', 'New Delhi', 'Delhi', 'NR'),
            ('MMCT', 'Mumbai Central', 'Mumbai', 'Maharashtra', 'WR'),
            ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal', 'ER'),
            ('SBC', 'KSR Bengaluru', 'Bengaluru', 'Karnataka', 'SWR'),
            ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu', 'SR'),
            ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat', 'WR'),
            ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh', 'NCR'),
            ('PNBE', 'Patna Junction', 'Patna', 'Bihar', 'ECR'),
            ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra', 'CR'),
            ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'Telangana', 'SCR'),
            ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir', 'NR'),
            ('BSB', 'Varanasi Junction', 'Varanasi', 'Uttar Pradesh', 'NR'),
            ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh', 'WCR'),
            ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'Uttar Pradesh', 'NER'),
            ('CDG', 'Chandigarh Junction', 'Chandigarh', 'Chandigarh', 'NR'),
        ]

        station_objs = {}
        for code, name, city, state, zone in stations_data:
            st, _ = Station.objects.update_or_create(
                code=code,
                defaults={'name': name, 'city': city, 'state': state, 'zone': zone}
            )
            station_objs[code] = st

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(station_objs)} stations."))

        # 3. Seed 12 Realistic Trains with Intermediate Stops and Classes
        trains_data = [
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
                'number': '12951',
                'name': 'Mumbai Tejas Rajdhani',
                'type': 'RAJDHANI',
                'src': 'MMCT', 'dest': 'NDLS',
                'dep': time(17, 0), 'arr': time(8, 32),
                'dist': 1384,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('MMCT', 1, None, time(17, 0), 0, 0, 0),
                    ('ADI', 2, time(21, 55), time(22, 5), 10, 492, 0),
                    ('BPL', 3, time(3, 15), time(3, 25), 10, 920, 1),
                    ('NDLS', 4, time(8, 32), None, 0, 1384, 1),
                ],
                'classes': [
                    ('1A', 'AC First Class', 2100, 2.40, 1, 24),
                    ('2A', 'AC 2-Tier', 1350, 1.75, 2, 48),
                    ('3A', 'AC 3-Tier', 900, 1.20, 4, 64),
                ]
            },
            {
                'number': '12952',
                'name': 'New Delhi Mumbai Rajdhani',
                'type': 'RAJDHANI',
                'src': 'NDLS', 'dest': 'MMCT',
                'dep': time(16, 55), 'arr': time(8, 35),
                'dist': 1384,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('NDLS', 1, None, time(16, 55), 0, 0, 0),
                    ('BPL', 2, time(22, 10), time(22, 20), 10, 464, 0),
                    ('ADI', 3, time(3, 20), time(3, 30), 10, 892, 1),
                    ('MMCT', 4, time(8, 35), None, 0, 1384, 1),
                ],
                'classes': [
                    ('1A', 'AC First Class', 2100, 2.40, 1, 24),
                    ('2A', 'AC 2-Tier', 1350, 1.75, 2, 48),
                    ('3A', 'AC 3-Tier', 900, 1.20, 4, 64),
                ]
            },
            {
                'number': '22436',
                'name': 'Vande Bharat Express',
                'type': 'VANDE_BHARAT',
                'src': 'NDLS', 'dest': 'BSB',
                'dep': time(6, 0), 'arr': time(14, 0),
                'dist': 759,
                'days': 'MON,TUE,WED,FRI,SAT,SUN',
                'stops': [
                    ('NDLS', 1, None, time(6, 0), 0, 0, 0),
                    ('CNB', 2, time(10, 8), time(10, 10), 2, 436, 0),
                    ('BSB', 3, time(14, 0), None, 0, 759, 0),
                ],
                'classes': [
                    ('CC', 'AC Chair Car', 650, 1.50, 6, 78),
                    ('1A', 'Executive Chair Car', 1350, 2.30, 2, 52),
                ]
            },
            {
                'number': '22435',
                'name': 'Varanasi Vande Bharat',
                'type': 'VANDE_BHARAT',
                'src': 'BSB', 'dest': 'NDLS',
                'dep': time(15, 0), 'arr': time(23, 0),
                'dist': 759,
                'days': 'MON,TUE,WED,FRI,SAT,SUN',
                'stops': [
                    ('BSB', 1, None, time(15, 0), 0, 0, 0),
                    ('CNB', 2, time(18, 30), time(18, 32), 2, 323, 0),
                    ('NDLS', 3, time(23, 0), None, 0, 759, 0),
                ],
                'classes': [
                    ('CC', 'AC Chair Car', 650, 1.50, 6, 78),
                    ('1A', 'Executive Chair Car', 1350, 2.30, 2, 52),
                ]
            },
            {
                'number': '12004',
                'name': 'Lucknow Shatabdi Express',
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
                    ('CC', 'AC Chair Car', 450, 1.10, 8, 78),
                    ('1A', 'Executive Class', 950, 1.80, 2, 46),
                ]
            },
            {
                'number': '12626',
                'name': 'Kerala Express',
                'type': 'SUPERFAST',
                'src': 'NDLS', 'dest': 'SBC',
                'dep': time(20, 10), 'arr': time(14, 30),
                'dist': 2390,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('NDLS', 1, None, time(20, 10), 0, 0, 0),
                    ('BPL', 2, time(5, 20), time(5, 30), 10, 700, 1),
                    ('HYB', 3, time(18, 10), time(18, 20), 10, 1540, 1),
                    ('SBC', 4, time(14, 30), None, 0, 2390, 2),
                ],
                'classes': [
                    ('2A', 'AC 2-Tier', 1200, 1.60, 2, 48),
                    ('3A', 'AC 3-Tier', 800, 1.10, 5, 64),
                    ('SL', 'Sleeper Class', 350, 0.45, 8, 72),
                ]
            },
            {
                'number': '12658',
                'name': 'Chennai Mail',
                'type': 'SUPERFAST',
                'src': 'SBC', 'dest': 'MAS',
                'dep': time(22, 40), 'arr': time(4, 15),
                'dist': 362,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('SBC', 1, None, time(22, 40), 0, 0, 0),
                    ('MAS', 2, time(4, 15), None, 0, 362, 1),
                ],
                'classes': [
                    ('1A', 'AC First Class', 850, 1.70, 1, 24),
                    ('2A', 'AC 2-Tier', 550, 1.30, 2, 48),
                    ('3A', 'AC 3-Tier', 380, 0.90, 4, 64),
                    ('SL', 'Sleeper Class', 180, 0.40, 6, 72),
                ]
            },
            {
                'number': '12009',
                'name': 'Mumbai Ahmedabad Shatabdi',
                'type': 'SHATABDI',
                'src': 'MMCT', 'dest': 'ADI',
                'dep': time(6, 20), 'arr': time(12, 45),
                'dist': 492,
                'days': 'MON,TUE,WED,THU,FRI,SAT',
                'stops': [
                    ('MMCT', 1, None, time(6, 20), 0, 0, 0),
                    ('ADI', 2, time(12, 45), None, 0, 492, 0),
                ],
                'classes': [
                    ('CC', 'AC Chair Car', 500, 1.15, 6, 78),
                    ('1A', 'Executive Chair Car', 1100, 1.90, 2, 46),
                ]
            },
            {
                'number': '12157',
                'name': 'Hutatma Express',
                'type': 'SUPERFAST',
                'src': 'PUNE', 'dest': 'MMCT',
                'dep': time(18, 0), 'arr': time(21, 55),
                'dist': 192,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('PUNE', 1, None, time(18, 0), 0, 0, 0),
                    ('MMCT', 2, time(21, 55), None, 0, 192, 0),
                ],
                'classes': [
                    ('CC', 'AC Chair Car', 260, 0.90, 3, 78),
                    ('2S', 'Second Sitting', 110, 0.35, 8, 108),
                ]
            },
            {
                'number': '12011',
                'name': 'Kalka Shatabdi Express',
                'type': 'SHATABDI',
                'src': 'NDLS', 'dest': 'CDG',
                'dep': time(7, 40), 'arr': time(11, 5),
                'dist': 266,
                'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
                'stops': [
                    ('NDLS', 1, None, time(7, 40), 0, 0, 0),
                    ('CDG', 2, time(11, 5), None, 0, 266, 0),
                ],
                'classes': [
                    ('CC', 'AC Chair Car', 320, 1.10, 6, 78),
                    ('1A', 'Executive Chair Car', 750, 1.80, 2, 46),
                ]
            },
        ]

        for tdata in trains_data:
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

            # Stops
            TrainStop.objects.filter(train=train).delete()
            for st_code, order, arr, dep, halt, dist, offset in tdata['stops']:
                TrainStop.objects.create(
                    train=train,
                    station=station_objs[st_code],
                    stop_order=order,
                    arrival_time=arr,
                    departure_time=dep,
                    halt_minutes=halt,
                    distance_from_source_km=dist,
                    day_offset=offset,
                )

            # Classes
            TrainClass.objects.filter(train=train).delete()
            for c_code, c_name, base, per_km, coaches, seats in tdata['classes']:
                TrainClass.objects.create(
                    train=train,
                    class_code=c_code,
                    class_name=c_name,
                    base_fare=base,
                    per_km_rate=per_km,
                    total_coaches=coaches,
                    seats_per_coach=seats,
                )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(trains_data)} trains with complete routes, stops, and class tariffs!"))
