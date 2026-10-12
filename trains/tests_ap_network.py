from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from datetime import date, timedelta
from trains.models import Station, Train, TrainStop, TrainClass
from bookings.models import Coach, Seat, JourneyInventory
from bookings.services import calculate_fare

class APNetworkDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Run seed command to populate the test database with the AP network
        call_command('seed_demo_data')

    def setUp(self):
        self.client = Client()

    def test_stations_seeded_count_and_presence(self):
        """Verify core AP stations and outside-AP anchors are seeded."""
        required_codes = [
            'BZA', 'TPTY', 'RU', 'VSKP', 'GNT', 'NLR', 'RJY', 'KRNT',
            'HX', 'ATP', 'OGL', 'EE', 'TEL', 'TDD', 'SLO', 'AKP',
            'VZM', 'CHE', 'NDL', 'GDR', 'CLX', 'NRT', 'MTM', 'CCT',
            'GTL', 'DMM', 'DHNE', 'SC', 'MAS', 'SBC'
        ]
        existing_codes = set(Station.objects.values_list('code', flat=True))
        for code in required_codes:
            self.assertIn(code, existing_codes, f"Station code {code} missing from database")

    def test_all_trains_stop_chronology_and_day_offset(self):
        """Verify that every train's stops follow strictly increasing time order with valid day offsets."""
        for train in Train.objects.filter(is_active=True):
            stops = list(train.stops.all().order_by('stop_order'))
            self.assertGreaterEqual(len(stops), 2, f"Train {train.train_number} has fewer than 2 stops")

            # First stop checks
            first_stop = stops[0]
            self.assertIsNone(first_stop.arrival_time, f"{train.train_number}: Origin arrival_time should be None")
            self.assertIsNotNone(first_stop.departure_time, f"{train.train_number}: Origin departure_time is None")
            self.assertEqual(first_stop.distance_from_source_km, 0, f"{train.train_number}: Origin distance must be 0")
            self.assertEqual(first_stop.day_offset, 0, f"{train.train_number}: Origin day_offset must be 0")

            # Last stop checks
            last_stop = stops[-1]
            self.assertIsNotNone(last_stop.arrival_time, f"{train.train_number}: Terminus arrival_time is None")
            self.assertIsNone(last_stop.departure_time, f"{train.train_number}: Terminus departure_time should be None")
            self.assertGreater(last_stop.distance_from_source_km, 0, f"{train.train_number}: Terminus distance must be > 0")

            # Intermediate sequence chronology
            prev_total_dep_minutes = first_stop.day_offset * 1440 + first_stop.departure_time.hour * 60 + first_stop.departure_time.minute

            for idx in range(1, len(stops)):
                curr_stop = stops[idx]
                arr_total_minutes = curr_stop.day_offset * 1440 + curr_stop.arrival_time.hour * 60 + curr_stop.arrival_time.minute
                
                self.assertGreater(
                    arr_total_minutes,
                    prev_total_dep_minutes,
                    f"Train {train.train_number} Stop #{curr_stop.stop_order} ({curr_stop.station.code}) arrival ({arr_total_minutes}m) is not strictly after previous departure ({prev_total_dep_minutes}m)"
                )

                if curr_stop.departure_time is not None:
                    dep_total_minutes = curr_stop.day_offset * 1440 + curr_stop.departure_time.hour * 60 + curr_stop.departure_time.minute
                    self.assertGreaterEqual(
                        dep_total_minutes,
                        arr_total_minutes,
                        f"Train {train.train_number} Stop #{curr_stop.stop_order} departure is earlier than arrival"
                    )
                    prev_total_dep_minutes = dep_total_minutes

    def test_cumulative_distances_strictly_increasing(self):
        """Verify station distances strictly increase along each train's route."""
        for train in Train.objects.filter(is_active=True):
            stops = list(train.stops.all().order_by('stop_order'))
            prev_dist = -1
            for stop in stops:
                self.assertGreater(
                    stop.distance_from_source_km,
                    prev_dist,
                    f"Train {train.train_number} distance at stop #{stop.stop_order} ({stop.station.code}) did not increase ({stop.distance_from_source_km} <= {prev_dist})"
                )
                prev_dist = stop.distance_from_source_km

    def test_no_duplicate_stations_within_train(self):
        """Verify no station is listed more than once in any train's timetable."""
        for train in Train.objects.filter(is_active=True):
            station_ids = list(train.stops.values_list('station_id', flat=True))
            self.assertEqual(
                len(station_ids),
                len(set(station_ids)),
                f"Train {train.train_number} contains duplicate stations in its stops"
            )

    def test_fares_positive_and_increasing_with_distance(self):
        """Verify that fares calculated between stops are positive and increase with distance."""
        train = Train.objects.filter(train_number='92801').first() # VSKP to MAS
        self.assertIsNotNone(train)
        
        stops = list(train.stops.all().order_by('stop_order'))
        vskp = stops[0].station
        rjy = stops[3].station   # ~201 km
        bza = stops[6].station   # ~350 km
        mas = stops[-1].station  # ~780 km

        fare_short, dist_short = calculate_fare(train, 'SL', vskp, rjy)
        fare_med, dist_med = calculate_fare(train, 'SL', vskp, bza)
        fare_long, dist_long = calculate_fare(train, 'SL', vskp, mas)

        self.assertGreater(fare_short, 0)
        self.assertGreater(fare_med, fare_short)
        self.assertGreater(fare_long, fare_med)
        self.assertLess(dist_short, dist_med)
        self.assertLess(dist_med, dist_long)

    def test_seeding_idempotence(self):
        """Verify running seed_demo_data multiple times does not duplicate records."""
        st_count_1 = Station.objects.count()
        tr_count_1 = Train.objects.count()
        stop_count_1 = TrainStop.objects.count()
        class_count_1 = TrainClass.objects.count()
        coach_count_1 = Coach.objects.count()
        seat_count_1 = Seat.objects.count()
        inv_count_1 = JourneyInventory.objects.count()

        # Run command second time
        call_command('seed_demo_data')

        self.assertEqual(Station.objects.count(), st_count_1)
        self.assertEqual(Train.objects.count(), tr_count_1)
        self.assertEqual(TrainStop.objects.count(), stop_count_1)
        self.assertEqual(TrainClass.objects.count(), class_count_1)
        self.assertEqual(Coach.objects.count(), coach_count_1)
        self.assertEqual(Seat.objects.count(), seat_count_1)
        self.assertEqual(JourneyInventory.objects.count(), inv_count_1)

    def test_ap_search_routes(self):
        """Verify searches for all required key route pairs return valid matching trains."""
        # Pick dates in the next 14 days covering all weekdays
        today = date.today()
        # Find next Monday to test daily & Mon-Wed-Fri trains
        next_mon = today + timedelta(days=((0 - today.weekday()) % 7 or 7))
        date_str = next_mon.isoformat()

        test_pairs = [
            ('BZA', 'TPTY', 'Vijayawada to Tirupati'),
            ('VSKP', 'BZA', 'Visakhapatnam to Vijayawada'),
            ('GNT', 'TPTY', 'Guntur to Tirupati'),
            ('KRNT', 'TPTY', 'Kurnool City to Tirupati'),
            ('NLR', 'RJY', 'Nellore to Rajahmundry'),
            ('HX', 'SBC', 'Kadapa to Bengaluru'),
            ('ATP', 'SBC', 'Anantapur to Bengaluru'),
            ('VSKP', 'MAS', 'Visakhapatnam to Chennai Central'),
            ('BZA', 'SC', 'Vijayawada to Secunderabad'),
        ]

        for from_code, to_code, label in test_pairs:
            response = self.client.get(reverse('trains:search'), {
                'from_station': from_code,
                'to_station': to_code,
                'journey_date': date_str,
            })
            self.assertEqual(
                response.status_code, 200,
                f"Search failed for {label} ({from_code} -> {to_code})"
            )
            matching_trains = response.context.get('matching_trains', [])
            self.assertGreater(
                len(matching_trains), 0,
                f"No trains found for {label} ({from_code} -> {to_code}) on {date_str}"
            )
