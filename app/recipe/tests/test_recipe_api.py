"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

# from core.models import Recipe
from core.models import (
    Recipe,
    Tag,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """Create and return a new user."""
    # as we added new tests and require more users in testing
    # build a helper function to create user
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    # set up a client and force authenticate this user
    # def setUp(self):
    #     self.client = APIClient()
    #     self.user = get_user_model().objects.create_user(
    #         'user@example.com',
    #         'testpass123',
    #     )
    #     self.client.force_authenticate(self.user)

    # Since we added more tests and those tests require to have more users, so user helper function to keep codes concise
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # also test the order of recipe list
        # retrieve recipes
        recipes = Recipe.objects.all().order_by('-id')

        # many = True, pass in a list of items
        serializer = RecipeSerializer(recipes, many=True)
        # validate it successfully retrives recipes
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # validate data match with what was created using create_recipe()
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )

        # keep codes concise with a helper function
        other_user = create_user(email='other@example.com', password='test123')

        # create a recipe for another unauthorized user
        create_recipe(user=other_user)
        # create a recipe for the authenticated user that was created in setup()
        create_recipe(user=self.user)

        # get request to the url RECIPES_URL
        res = self.client.get(RECIPES_URL)

        # retrieve the data for self.user from the database
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check if data retrieved and filtered for self.user matches res.data(the results of get request of url RECIPES_URL)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        # create a recipe that belongs to self.user
        recipe = create_recipe(user=self.user)

        # create a detail url of this recipe
        url = detail_url(recipe.id)
        # res is the response from a get request to this url
        res = self.client.get(url)
        # remember self.client is the APIClient(), it mocks the behavior of a real client

        # validate RecipeDetailSerialier => Build the RecipeDetailSerialier
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        # test the create recipe function, so don't use create_recipe(user = self.user) to create a recipe
        # instead pass in payload
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        # To create a recipe is the same as to post the recipe url # /api/recipes/recipe
        # post request
        res = self.client.post(RECIPES_URL, payload)
        # success response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            # use payload.key k to retrieve value from recipe and compare it with v from payload.value
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user, # an authenticated user
            title='Sample recipe title',
            link=original_link,
        )


        # updates to show, here we only want to update title
        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        # update recipe at url with payload
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # by default, db won't be refreshed so we need to refresh it to show the updates( done with a patch request)
        recipe.refresh_from_db()
        # validate that after sending patch request, change on title of the recipe matches payload['title']
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        # since self.user is an authenticated user, therefore the recipe's owner(or user) should match with self.user
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://exmaple.com/recipe.pdf',
            description='Sample recipe description.',
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        # put request is for full update to update every single field
        res = self.client.put(url, payload)

        # validate success from put request
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # fresh db to show the updates
        recipe.refresh_from_db()

        # pass in key k to retrieve value v from recipe
        # compare value v to what's in payload.value to validate put request
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        # confirm that the user of this recipe matchs the self.user as this's a put request from an authenticated user
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        # test delete request
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # valid .exists() returns False
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        # new_user is another user that self.user has not access to
        # therefore recipe created by new_user can not be deleted by self.user
        # recipe.id is the id of recipe belonging to new_user
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

# # Create Tag API, Step 12: Add tests in test_recipe_api because we want recipe api to support tag features
# session 99
    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # Double check the length is 1 then recipe = recipes[0],
        # otherwise if it wasn't successfully created, it returns a generic index error instead of testing our features
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        # payload for new recipe
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],# new tag
        }
        # post request
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            # filter from all tags to locate tags belonging to self.user with name = tag['name']
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists() # make sure it exists
            self.assertTrue(exists) # make sure it returns True
    # Run test and failed
    # Response from test:
# Traceback (most recent call last):
#   File "/app/recipe/tests/test_recipe_api.py", line 303, in test_create_recipe_with_existing_tags
#     self.assertEqual(recipe.tags.count(), 2)
# AssertionError: 0 != 2

#     Traceback (most recent call last):
#   File "/app/recipe/tests/test_recipe_api.py", line 278, in test_create_recipe_with_new_tags
#     self.assertEqual(recipe.tags.count(), 2)
# AssertionError: 0 != 2
