from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    def setUp(self):
        self.register_user_url = reverse_lazy('register_user')

    def test_create_account(self):
        data = {'username': 'user1', 'password': 'password'}
        response = self.client.post(self.register_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_account_missed_fields(self):
        data = {'password': 'password'}
        response = self.client.post(self.register_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertNotIn('password', response.data)

        data = {'username': 'username'}
        response = self.client.post(self.register_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('username', response.data)
        self.assertIn('password', response.data)

        data = {}
        response = self.client.post(self.register_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('username', response.data)

    def test_create_existing_username(self):
        self.test_create_account()
        data = {'username': 'user1', 'password': 'password'}
        response = self.client.post(self.register_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('A user with that username already exists.', str(response.data.get('username')[0]))

    def test_create_password_blank(self):
        data = {'username': 'user1', 'password': ''}
        response = self.client.post(self.register_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank', str(response.data.get('password')[0]))


class LoginTests(APITestCase):
    def setUp(self):
        register_user_url = reverse_lazy('register_user')
        data = {'username': 'user1', 'password': 'password'}
        _ = self.client.post(register_user_url, data, format='json')
        self.login_user_url = reverse_lazy('login_user')

    def test_login(self):
        data = {'username': 'user1', 'password': 'password'}
        response = self.client.post(self.login_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Why do we have this status 201?
        self.assertIn('token', response.data)

    def test_login_wrong_credentials(self):
        data = {'username': 'user1', 'password': 'password2'}
        response = self.client.post(self.login_user_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)


class VerifyTokenTests(APITestCase):
    """
    If use this service as a separate microservice might need to
    check if token valid from external microservice
    """
    def setUp(self):
        register_user_url = reverse_lazy('register_user')
        data = {'username': 'user1', 'password': 'password'}
        self.response_with_token = self.client.post(register_user_url, data, format='json')
        self.verify_token_url = reverse_lazy('verify_token')

    def test_verify_token(self):
        data = {'token': self.response_with_token.data.get('token', '')}
        response = self.client.post(self.verify_token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_verify_token_fail(self):
        data = {'token': 'wrong token'}
        response = self.client.post(self.verify_token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token(self):
        refresh_token_url = reverse_lazy('refresh_token')
        data = {'token': self.response_with_token.data.get('token', '')}
        response = self.client.post(refresh_token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)


class AccessSecureResourceTests(APITestCase):
    def setUp(self):
        register_user_url = reverse_lazy('register_user')
        data = {'username': 'user1', 'password': 'password'}
        response = self.client.post(register_user_url, data, format='json')
        self.token = response.data.get('token')
        self.secure_resource_url = reverse_lazy('secure_endpoint')

    def test_access_secure_resource(self):
        response = self.client.get(self.secure_resource_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Why do we have this status 201?
        self.assertIn('ok', response.data)

    def test_fail_access_secure_resource(self):
        response = self.client.get(self.secure_resource_url, HTTP_AUTHORIZATION=f'Bearer invalid_token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('ok', response.data)


class UserUpdateTests(APITestCase):
    def setUp(self):
        register_user_url = reverse_lazy('register_user')
        data = {'username': 'user1', 'password': 'password'}
        response = self.client.post(register_user_url, data, format='json')
        self.token = response.data.get('token')
        self.user_url = reverse_lazy('manage_user')

    def test_user_get_own_info(self):
        response = self.client.get(self.user_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

    def test_user_update(self):
        new_first_name = 'new_first_name'
        data = {'first_name': new_first_name}
        response = self.client.patch(self.user_url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('new_first_name', response.data.get('first_name'))

    def test_user_update_fail(self):
        response = self.client.patch(self.user_url, data={}, HTTP_AUTHORIZATION=f'Bearer invalid_token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_delete(self):
        # verify that user exists and can receive own info
        self.test_user_get_own_info()

        # user delete himself
        response = self.client.delete(self.user_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # verify that user is no longer available
        response = self.client.get(self.user_url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
