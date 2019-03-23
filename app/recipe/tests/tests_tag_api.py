# import get_user_model
from django.contrib.auth import get_user_model
# import reverse for generating the url
from django.urls import reverse
from django.test import TestCase

# imports from rest_framework for testing
from rest_framework import status
from rest_framework.test import APIClient

# model( Tag ) and serializer for that model
from core.models import Tag
from recipe.serializers import TagSerializer

# create tag's url ( for api calls )
TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags api"""

    def setUp(self):
        # create a new user
        self.user = get_user_model().objects.create(
            email="test@ram.com",
            password="test123"
        )
        # authenticate the user(force_authenticate) with APIClient
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        # create a couple of tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # get the response from the APIClient. ( authenticated )
        res = self.client.get(TAGS_URL)

        # order the tags by name
        tags = Tag.objects.all().order_by('-name')
        # create a serializer for the above querySets
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        # first, create a different user
        user2 = get_user_model().objects.create(
            email="testother@ram.com",
            password="test123"
        )
        # create a tag of this user in the Tags model
        Tag.objects.create(user=user2, name='Grief')
        # create a tag for our authenticated user
        tag = Tag.objects.create(user=self.user, name='Ayvak Food')

        # get the response from the ApiClient
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check the length instead of data first
        self.assertEqual(len(res.data), 1)

        # check for the data
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        # see if the tag is created in the user
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
