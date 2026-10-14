from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testpassenger',
            email='test@example.com',
            password='Password@123',
            first_name='Rahul',
            last_name='Sharma'
        )

    def test_profile_auto_created(self):
        """Verify that a Profile is automatically created via post_save signal."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)

    def test_user_registration_view(self):
        """Test registration flow."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'Ankit',
            'last_name': 'Verma',
            'phone_number': '9876543210',
            'id_proof_type': 'AADHAAR',
            'id_proof_number': '1234-5678-9012',
            'password': 'StrongPass@123',
            'confirm_password': 'StrongPass@123',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.profile.phone_number, '9876543210')

    def test_login_and_logout(self):
        """Test authentication login and logout."""
        login_success = self.client.login(username='testpassenger', password='Password@123')
        self.assertTrue(login_success)

        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit(self):
        """Test updating profile details."""
        self.client.login(username='testpassenger', password='Password@123')
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Rahul Updated',
            'last_name': 'Sharma',
            'email': 'test@example.com',
            'phone_number': '9988776655',
            'address': '123 Station Road',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'id_proof_type': 'PAN',
            'id_proof_number': 'ABCDE1234F',
            'emergency_contact_name': 'Father',
            'emergency_contact_phone': '9112233445',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Rahul Updated')
        self.assertEqual(self.user.profile.city, 'New Delhi')

    def test_register_redirects_to_login_with_message(self):
        """Register success: redirect to login with 'Account created. Please log in.' and do not auto-login."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'reguser',
            'email': 'reguser@example.com',
            'first_name': 'Reg',
            'last_name': 'User',
            'phone_number': '9988776611',
            'id_proof_type': 'AADHAAR',
            'id_proof_number': '1111-2222-3333',
            'password': 'PassReg@123',
            'confirm_password': 'PassReg@123',
        }, follow=True)

        self.assertRedirects(response, reverse('accounts:login'))
        messages_list = [m.message for m in response.context['messages']]
        self.assertIn("Account created. Please log in.", messages_list)
        # Verify user is NOT auto-logged in
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_redirect_with_safe_next(self):
        """Login success: redirect to safe next URL if present."""
        target_next = '/bookings/pnr-lookup/'
        response = self.client.post(f"{reverse('accounts:login')}?next={target_next}", {
            'username': 'testpassenger',
            'password': 'Password@123',
            'next': target_next,
        })
        self.assertRedirects(response, target_next)

    def test_login_redirect_without_next_to_book_ticket(self):
        """Login success without next: redirect to Book Ticket (core:home)."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testpassenger',
            'password': 'Password@123',
        })
        self.assertRedirects(response, reverse('core:home'))

    def test_guest_booking_redirect_to_login_and_back(self):
        """Guest booking click: redirect to login?next=<original url> and back after login."""
        import urllib.parse
        booking_url = '/bookings/new/?train=12302&class_code=3A&journey_date=2026-10-20&from_station=NDLS&to_station=HWH'
        response = self.client.get(booking_url)
        self.assertEqual(response.status_code, 302)
        expected_login_redirect = f"{reverse('accounts:login')}?next={urllib.parse.quote(booking_url)}"
        self.assertRedirects(response, expected_login_redirect, fetch_redirect_response=False)

        # Log in with the next param
        login_response = self.client.post(f"{reverse('accounts:login')}?next={urllib.parse.quote(booking_url)}", {
            'username': 'testpassenger',
            'password': 'Password@123',
            'next': booking_url,
        })
        self.assertRedirects(login_response, booking_url, fetch_redirect_response=False)

    def test_logout_redirect_to_home_with_message(self):
        """Logout: redirect to Home with 'You have been logged out.'"""
        self.client.login(username='testpassenger', password='Password@123')
        response = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertRedirects(response, reverse('core:home'))
        messages_list = [m.message for m in response.context['messages']]
        self.assertIn("You have been logged out.", messages_list)

    def test_authenticated_user_visiting_login_or_register_redirects(self):
        """Already logged-in users visiting login or register redirect to Book Ticket (core:home)."""
        self.client.login(username='testpassenger', password='Password@123')
        
        login_resp = self.client.get(reverse('accounts:login'))
        self.assertRedirects(login_resp, reverse('core:home'))

        register_resp = self.client.get(reverse('accounts:register'))
        self.assertRedirects(register_resp, reverse('core:home'))
