from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# reverse(app_name:identifier)
RECIPE_URL = reverse('recipe:recipe-list')


# helper functions to create he urls
# list   : /api/recipe/recipes
# detail : /api/recipe/recipes/1
def detail_url(recipe_id):
    """Return recipe detail url"""
    # recipe-detail is the app_name added by default Router.
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    """create and reuturn a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamen'):
    """create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


# ccreate a sample recipe
def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # update our defaults with params( if any )
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeTests(TestCase):
    """Test unauthenticated requests to Recipe API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authorization is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test recipeis can be received by authorized users"""
    def setUp(self):
        # create a user
        self.user = get_user_model().objects.create(
            email="test@ram.com",
            password="testawe"
        )
        # force_authenticate the user
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving all the recipes"""
        # create some recipe's first
        sample_recipe(user=self.user)
        sample_recipe(user=self.user, title="Another recipe")

        # prepare the serialzer from the quertset
        # It is easier preparing our own data for those two recipies
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        # try to get the response from the APIclient( authenticated)
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes of an authenticated user"""
        # create a different user
        user2 = get_user_model().objects.create_user(
            'other@am.cm',
            'adededs'
        )
        # create a recipe by user2
        sample_recipe(user=user2)
        # create one recipe by this authenticated user
        sample_recipe(user=self.user)

        # get recipes create by our authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        # get the response by client( user authenticated )
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(self.user)
        # add tag and ingredient to this recipe
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        # generate the detail recipe url with this id
        url = detail_url(recipe.id)
        res = self.client.get(url)

        # we create the data with serializer
        serializer = RecipeDetailSerializer(recipe)  # many is not required
        self.assertEqual(res.data, serializer.data)
