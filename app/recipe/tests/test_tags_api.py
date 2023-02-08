# Create Tag API, Step 5: Implement API for listing tags. But before that create tests then create implmentations
# Add tests in core/test_tags_api.py

# Run test using docker-compose run --rm app sh -c "python manage.py test"
# Response from test
# ImportError: cannot import name 'TagSerializer' from 'recipe.serializers' (/app/recipe/serializers.py)
# Create Tag API, Step 6: Create TagSerializer in recipe/serializers.py

"""
Tests for the tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status # status code check
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer # create it in Create Tag API, Step 5


TAGS_URL = reverse('recipe:tag-list')

# Create Tag API, Step 8: Add a test for updating tags
def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])

# typical way to create an user
def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        # force authenticating self.user
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        # create some Tag objects
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Run get request to the testing endpoint, TAGS_URL is defined in ___
        res = self.client.get(TAGS_URL)

        # Since we need to compare and validate data from the serializer matches data from get request response
        # We need to make sure they're in a certain order
        tags = Tag.objects.all().order_by('-name') # tags are what we just added from above
        # many=True, allow many tags for one recipe
        # TagSerializer hasn't been created yet, but TDD
        # Pass in tag objects just added above to TagSerializer
        serializer = TagSerializer(tags, many=True)
        # check get request succeeded
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # data matches
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        # Test whether get request returns tags belonging to self.user

        # test whether other users can access self.user's tags
        # create another user
        user2 = create_user(email='user2@example.com')
        # create a tag for antoher user
        Tag.objects.create(user=user2, name='Fruity')
        # create a tag for self.user
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        # get request
        res = self.client.get(TAGS_URL)
        # successfully pass in get request
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        # Since the lastest created tag is from self.user
        # tag, which refers to the self.user tag, should matches response from self.client.get()
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    # Create Tag API, Step 8: Add tests for updating tags
    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db() # after patch request(request for update), refresh database to show updates
        self.assertEqual(tag.name, payload['name'])

    # Run test in the terminal
    # Response from the test
    # django.urls.exceptions.NoReverseMatch: Reverse for 'tag-detail' not found. 'tag-detail' is not a valid view function or pattern name.
    # Next, implement this functionality
    # Open recipe/views.py

    # Create Tag API, Step 10: Write tests for deleting tags
    def test_delete_tag(self):
        """Test deleting a tag."""
        # create one tag
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url) # delete request

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the tag for self.user were deleted
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
    # Run test
    # Response from the test:
#     Traceback (most recent call last):
#   File "/app/recipe/tests/test_tags_api.py", line 129, in test_delete_tag
#     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
# AssertionError: 405 != 204

    # Next, implete delete tag API
    # Open views.py
