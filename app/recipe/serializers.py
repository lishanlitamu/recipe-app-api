"""
Serializers for recipe APIs
"""
from rest_framework import serializers

# from core.models import Recipe
from core.models import (
    Recipe,
    Tag,
)

# Create Tag API, Step 6: Create TagSerializer in recipe/serializers.py (Implement tag listing API)
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag # from core.models import Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

# open recipe/views.py


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # Create Tag API, Step 13: Implement create tag feature
    # Use nested serializer, session 100
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # fields = ['id', 'title', 'time_minutes', 'price', 'link']
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    # Create Recipe API Step 14: Change create() method in recipe/serializers.py to support update feature
    # after this step, run "docker compose up" to run server,
    # you should see "Running migrations:..."
    # Open browser "http://127.0.0.1:8000/api/docs/#/"
    # first authenticate a user, user => /api/user/create/  => a post request
    # get token from user => post => api/user/token/
    # login using authorize user tag at the top
    # post /api/recipe/recipes/

    # or go to 127.0.0.1:8000/admin
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        # instance is the existing instance
        tags = validated_data.pop('tags', None) # if not available returns None
        if tags is not None:
            # empty list is not None, so clear it first
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    # commented out for Step 14, change create() method to include update feature
    # # override create()
    # # create receipe with custom setting
    # def create(self, validated_data):
    #     """Create a recipe."""
    #     # get and remove it from data base => use .pop()
    #     tags = validated_data.pop('tags', [])
    #     recipe = Recipe.objects.create(**validated_data)
    #     auth_user = self.context['request'].user
    #     for tag in tags:
    #         tag_obj, created = Tag.objects.get_or_create(
    #             user=auth_user,
    #             **tag,
    #         )
    #         recipe.tags.add(tag_obj)

    #     return recipe
    # # For Step 13, Run test and pass

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

# RecipeDetailSerializer is an extension of RecipeSerialier therefore use it as the base class
# Add extra fields
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        # just add one field 'description'

# # Session 100, move this up then reference it in RecipeSerializer, nested serializer
# # Create Tag API, Step 6: Create TagSerializer in recipe/serializers.py (Implement tag listing API)
# class TagSerializer(serializers.ModelSerializer):
#     """Serializer for tags."""

#     class Meta:
#         model = Tag # from core.models import Tag
#         fields = ['id', 'name']
#         read_only_fields = ['id']

# # open recipe/views.py

