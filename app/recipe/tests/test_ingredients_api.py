# import usser ( we use this for authentication )
from django.contrib.auth import get_user_model
# import reverse to generate urls from app_name
from django.urls import reverse
# import testcase from test module
from django.test import TestCase

# import status( for status codes ) and APIClient (to make requests)
from rest_framework import status
from rest_framework.test import APIClient

# import our models from core
from core.models import Ingredient

# import our modelSerializer from our recipe app
from recipe.serializers import IngredientSerializer


# create the url for our ingredient-list
INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        """add apiclient for testing public apis"""
        self.client = APIClient()

    def test_login_required(self):
        """Test that authorization is required for retrieving tags"""
        # get the response from this client( un authorized )
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test ingredients can be retrieved by authorized user"""

    def setUp(self):
        # create a user
        self.user = get_user_model().objects.create(
            email="test@eam.com",
            password="passwe"
        )
        # create a client and authenticate the user
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        # first , create some ingredients
        Ingredient.objects.create(user=self.user, name="first")
        Ingredient.objects.create(user=self.user, name="second")

        # get the objects from database
        ingredients = Ingredient.objects.all().order_by('-name')
        # get the serializer object
        serializer = IngredientSerializer(ingredients, many=True)

        # get the response with this apiclient( authnticated )
        res = self.client.get(INGREDIENTS_URL)

        # check the status\
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check if we are gettig same data from serializer
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients for authenticated users are returned"""
        # create a new user and add some ingredients for this user
        user2 = get_user_model().objects.create_user('other@ram.com',
                                                     'tset123')
        # cerate few tags for this new user
        Ingredient.objects.create(user=user2, name="ing1")

        # create an ingredient for our authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name="ing_ori")

        # get the response
        res = self.client.get(INGREDIENTS_URL)

        # test the response code
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
