"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # add tags
    tags = models.ManyToManyField('Tag')
    # Create Ingredients API, Step 2, add ingredient object to core/models.py
    # add Ingredients
    ingredients = models.ManyToManyField('Ingredient')

    def __str__(self):
        return self.title

# Create Tag API, Step 2: Create a tag object in core.models
class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        # if user is deleleted, tags will be deleted.
    )

    def __str__(self):
        return self.name

# Create Tag API, Step 3: Add tags in migrations
# open terminal
# docker-compose run --rm app sh -c "python manage.py makemigrations"
# response back:
# Migrations for 'core':
#   core/migrations/0003_auto_20230208_2035.py
#     - Create model Tag
#     - Add field tags to recipe

# See core/migrations/0003_auto.../
# migrations.AddField(
#             model_name='recipe',
#             name='tags', # added field tags to recipe
#             field=models.ManyToManyField(to='core.Tag'),
#         ),

# Create Tag API, Step 4: Register models.Tag to core/admin.py

# Create Tag API, Step 5: Implement API for listing tags. But before that create tests then create implmentations
# Add tests in core/test_tags_api.py


# Create Ingredients API, Step 2
class Ingredient(models.Model):
    """Ingredient for recipes."""
    #
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

# then create the migrate files for this new model
# open terminal
# docker-compose run --rm app sh -c "python manage.py makemigrations"
# response in terminal
# Migrations for 'core':
#   core/migrations/0004_auto_20230214_0334.py
#     - Create model Ingredient
#     - Add field ingredients to recipe
# Then go to core/admin.py to add admin.site.register(models.Ingredient)