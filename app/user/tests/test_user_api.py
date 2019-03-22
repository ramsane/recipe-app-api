from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# import some helper functions from rest framework
from rest_framework.test import APIClient
from rest_framework import status

# create create user url using reverse
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


# helper function to create some users for testing
def create_user(**params):
    return get_user_model().objects.create_user(**params)


# to test for something which is not authenticated.( like create user )
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        """Just create an APIClient which we can use it for all of our tests"""
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid paylod is successful"""
        # create a payload for this APi
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # get the response from the api
        res = self.client.post(CREATE_USER_URL, payload)
        # test the status code
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # test if object is actually created in the database
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # check if password is not returned in the status object
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists failed"""
        # create a payload
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        create_user(**payload)
        # get the response from creat_user_url
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {'email': 'test@gmail.com', 'password': 'ps'}
        res = self.client.post(CREATE_USER_URL, payload)

        # make sure that it returns the http bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that user was never created..
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that the token is created for the user"""
        # create the payload
        payload = {'email': 'ram@gam.com', 'password': 'tese123'}
        # create the user
        create_user(**payload)
        # authenticate the user with APIClient from rest framework
        res = self.client.post(TOKEN_URL, payload)

        # see if we have token in the response.
        self.assertIn('token', res.data)
        # see if status code is ok
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        # create the user
        create_user(email='ram@gami.cpm', password='1234')
        # authenticate with invalid credentials
        res = self.client.post(TOKEN_URL,
                               {'email': 'ram@gami.cpm', 'password': '123'})

        # make sure that the token is not in the response
        self.assertNotIn('token', res.data)
        # check the status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that the token is not created when the user doesn't exists"""
        payload = {'email': 'ram@gmail.com', 'password': 'dse'}
        # get the response from the APIClient ( from rest_framework )
        res = self.client.post(TOKEN_URL, payload)

        # make sure that the token is not in the response
        self.assertNotIn('token', res.data)
        # check the 400 bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that password and email are required"""
        # response for missing password
        res_no_password = self.client.post(TOKEN_URL,
                                           {'email': 'ram@gmail.com',
                                            'password': ''})

        # make sure that the token is not in the response
        self.assertNotIn('token', res_no_password.data)
        # check the 400 bad request
        self.assertEqual(res_no_password.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API that requires user authentication"""

    def setUp(self):
        # create the user for this tests
        self.user = create_user(
            email='test@gmail.com',
            password='test124',
            name='name'
        )
        # create an APIClient for this test
        self.client = APIClient()
        # authentocate this user with force_authenticate
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retreiving profile for logged in user"""
        # since we already authenticated user, we can just get his profile
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that post is not allowed on thisi url"""
        # get the response from post request directly.
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword'}

        # get response from the pach request from the uesr who is authenticated
        res = self.client.patch(ME_URL, payload)
        # get the values from the updated database
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
