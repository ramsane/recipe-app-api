from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# import some helper functions from rest framework
from rest_framework.test import APIClient
from rest_framework import status

# create create user url using reverse
CREATE_USER_URL = reverse('user:create')


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
