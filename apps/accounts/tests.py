from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AccountsAPITestCase(APITestCase):
    def setUp(self):
        # Data used for registration endpoint
        self.registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        # Create a user directly for authenticated tests
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='authpass123',
            first_name='Auth',
            last_name='User'
        )

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login(self):
        data = {
            'email': 'auth@example.com',
            'password': 'authpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_profile(self):
        # Authenticate as created user to access profile
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile(self):
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_change_password(self):
        data = {
            'old_password': 'authpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('accounts:change-password'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deactivate_account(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('accounts:deactivate'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_delete_account(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('accounts:delete'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
