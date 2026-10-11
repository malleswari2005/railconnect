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
