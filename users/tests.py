from django.contrib.auth.models import User
from django.test import TestCase
from .models import Profile
# Create your tests here.
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from phonenumber_field.modelfields import PhoneNumber

class RegisterTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('users:user-register')
        existing_data = {
            "username": "existing",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "existing@gmail.com",
            "password": "1234",
            "confirm_password": "1234"
        }
        resp = self.client.post(self.url, existing_data)
        self.assertEquals(resp.status_code, 201)

    def test_user_registration_with_correct_data(self):
        data = {
            "username": "admin",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "admin@gmail.com",
            "password": "1234",
            "confirm_password": "1234"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 201)

    def test_registration_with_existing_username(self):
        data = {
            "username": "existing",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "new@gmail.com",
            "password": "1234",
            "confirm_password": "1234"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_registration_with_existing_email(self):
        data = {
            "username": "existingmail",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "existing@gmail.com",
            "password": "1234",
            "confirm_password": "1234"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_registration_with_invalid_email(self):
        data = {
            "username": "invalidgmail",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "invalidemail",
            "password": "1234",
            "confirm_password": "1234"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_registration_with_blank_username(self):
        data = {
            "username": "",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "blankusername@gmail.com",
            "password": "1234",
            "confirm_password": "1234"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_registration_with_blank_email(self):
        data = {
            "username": "blankemail",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "",
            "password": "1234",
            "confirm_password": "1234"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_registration_with_blank_password(self):
        data = {
            "username": "blankpaswd",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "blankpaswd@gmail.com",
            "password": "",
            "confirm_password": ""
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_registration_with_different_password(self):
        data = {
            "username": "paswd",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "password4@gmail.com",
            "password": "1234",
            "confirm_password": "12345"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)


class LoginTestCase(APITestCase):
    def setUp(self) -> None:
        # Register user for login test
        url = reverse('users:user-register')
        data = {
            "username": "admin",
            "first_name": "Admin",
            "last_name": "Ous",
            "email": "admin@gmail.com",
            "password": "1234",
            "confirm_password": "1234"
        }
        self.client.post(url, data)
        self.url = reverse('users:user-login')

    def test_login_with_correct_password(self):
        data = {"username": "admin", "password": "1234"}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)

    def test_login_with_wrong_password(self):
        data = {"username": "admin", "password": "wrong"}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_login_with_wrong_username(self):
        data = {"username": "wrong", "password": "1234"}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_login_with_blank_password(self):
        data = {"username": "admin", "password": ""}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_login_with_blank_username(self):
        data = {"username": "", "password": ""}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)


class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
        )
        self.profile = self.user.profile

    def test_profile_creation(self):
        """Test that a Profile instance is created when a User instance is created."""
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)

    def test_create_profile_signal(self):
        """Test that the create_profile signal creates a Profile instance when a User instance is created."""
        user = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpassword2',
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_phone_number_field(self):
        """Test that the phone_number field is a PhoneNumber instance."""
        phone_number = '+1234567890'
        self.profile.phone_number = phone_number
        self.assertIsInstance(self.profile.phone_number, PhoneNumber)
        self.assertEqual(str(self.profile.phone_number), phone_number)