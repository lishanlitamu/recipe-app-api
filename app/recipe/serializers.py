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

    # override create()
    # create receipe with custom setting
    def create(self, validated_data):
        """Create a recipe."""
        # get and remove it from data base => use .pop()
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

        return recipe
    # For Step 13, Run test and pass

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

