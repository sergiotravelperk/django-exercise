from django.test import TestCase

from core import models


class ModelTests(TestCase):

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            name='Steak and mushroom sauce',
            description='Steak and mushroom sauce'
        )

        self.assertEqual(str(recipe), recipe.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        recipe = models.Recipe.objects.create(
            name='Steak and mushroom sauce',
            description='Steak and mushroom sauce'
        )

        ingredient = models.Ingredient.objects.create(
            name='Cucumber',
            recipe=recipe
        )

        self.assertEqual(str(ingredient), ingredient.name)
