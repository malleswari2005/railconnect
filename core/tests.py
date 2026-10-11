from django.test import TestCase, Client
from django.urls import reverse

class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'RailConnect')
        self.assertContains(response, 'Find Trains')

    def test_about_page_loads(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About RailConnect')
        self.assertContains(response, '5-Member Team Module Division')

    def test_custom_404_page(self):
        response = self.client.get('/non-existent-railway-route-404/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Track Not Found!', status_code=404)
