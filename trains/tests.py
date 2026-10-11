from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta, time
from trains.models import Station, Train, TrainStop, TrainClass

class TrainsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.st1 = Station.objects.create(code='NDLS', name='New Delhi', city='Delhi', state='Delhi')
        self.st2 = Station.objects.create(code='CNB', name='Kanpur Central', city='Kanpur', state='UP')
        self.st3 = Station.objects.create(code='HWH', name='Howrah Jn', city='Kolkata', state='WB')

        self.train = Train.objects.create(
            train_number='12302',
            name='Kolkata Rajdhani',
            train_type='RAJDHANI',
            source_station=self.st1,
            destination_station=self.st3,
            departure_time=time(16, 55),
            arrival_time=time(9, 55),
            distance_km=1450,
            runs_on_days='MON,TUE,WED,THU,FRI,SAT,SUN',
        )

        TrainStop.objects.create(train=self.train, station=self.st1, stop_order=1, departure_time=time(16, 55), distance_from_source_km=0)
        TrainStop.objects.create(train=self.train, station=self.st2, stop_order=2, arrival_time=time(21, 30), departure_time=time(21, 40), distance_from_source_km=436)
        TrainStop.objects.create(train=self.train, station=self.st3, stop_order=3, arrival_time=time(9, 55), distance_from_source_km=1450, day_offset=1)

        TrainClass.objects.create(train=self.train, class_code='3A', class_name='AC 3 Tier', base_fare=950, per_km_rate=1.20)

    def test_station_uppercase(self):
        st = Station.objects.create(code='mas ', name='Chennai Central', city='Chennai', state='TN')
        self.assertEqual(st.code, 'MAS')

    def test_train_runs_on_day(self):
        self.assertTrue(self.train.runs_on_day('MON'))
        self.assertTrue(self.train.runs_on_day('mon'))

    def test_search_direct_route(self):
        future_date = (date.today() + timedelta(days=5)).isoformat()
        response = self.client.get(reverse('trains:search'), {
            'from_station': 'NDLS',
            'to_station': 'HWH',
            'journey_date': future_date,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kolkata Rajdhani')
        self.assertContains(response, '12302')

    def test_search_intermediate_route(self):
        """Intermediate stop: NDLS to CNB should match the train!"""
        future_date = (date.today() + timedelta(days=5)).isoformat()
        response = self.client.get(reverse('trains:search'), {
            'from_station': 'NDLS',
            'to_station': 'CNB',
            'journey_date': future_date,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '12302')

    def test_search_reverse_route_not_found(self):
        """Reverse travel (HWH to NDLS) on a train heading NDLS -> HWH should not appear."""
        future_date = (date.today() + timedelta(days=5)).isoformat()
        response = self.client.get(reverse('trains:search'), {
            'from_station': 'HWH',
            'to_station': 'NDLS',
            'journey_date': future_date,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Direct Trains Found')

    def test_search_same_station_rejection(self):
        future_date = (date.today() + timedelta(days=5)).isoformat()
        response = self.client.get(reverse('trains:search'), {
            'from_station': 'NDLS',
            'to_station': 'NDLS',
            'journey_date': future_date,
        })
        self.assertEqual(response.status_code, 302)

    def test_search_past_date_rejection(self):
        past_date = (date.today() - timedelta(days=1)).isoformat()
        response = self.client.get(reverse('trains:search'), {
            'from_station': 'NDLS',
            'to_station': 'HWH',
            'journey_date': past_date,
        })
        self.assertEqual(response.status_code, 302)
