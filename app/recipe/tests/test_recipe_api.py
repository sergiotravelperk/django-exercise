from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient

from recipe.serializers import RecipeSerializer, IngredientSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(recipe, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(recipe=recipe, name=name)


def sample_recipe(**params):
    """Create and return a sample recipe"""
    defaults = {
        'name': 'Sample recipe',
        'description': 'Description recipe',
    }
    defaults.update(params)

    return Recipe.objects.create(**defaults)


class PublicRecipeApiTests(TestCase):
    """Test public recipe API endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe()
        sample_recipe()

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_recipes_by_name(self):
        """Test returning recipes with specific name"""
        name = 'Chicken'

        recipe1 = sample_recipe(name='Chicken cacciatore')
        recipe2 = sample_recipe(name='Posh beans on toast')

        res = self.client.get(RECIPES_URL + '?name=' + name)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe()
        sample_ingredient(recipe)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'name': 'Chocolate cheesecake',
            'description': 'Chocolate is love',
            'ingredients': [{'name': 'Chocolate'}, {'name': 'Cheese'}, {
                'name': 'Love'}],
        }
        res = self.client.post(RECIPES_URL, payload, 'json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(payload['name'], recipe.name)
        self.assertEqual(payload['description'], recipe.description)
        self.assertEqual(recipe.ingredients.count(), 3)

    def test_update_recipe_without_ingredients(self):
        """Test updating a recipe without ingredients"""
        recipe = sample_recipe()
        sample_ingredient(recipe)

        payload = {'name': 'Pollo a la Brasa',
                   'description': 'Pollo a la Brasa'}
        url = detail_url(recipe.id)
        self.client.patch(url, payload, 'json')

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        self.assertEqual(recipe.ingredients.count(), 1)

    def test_update_recipe_with_ingredients(self):
        """Test updating a recipe with ingredients"""
        recipe = sample_recipe()
        ingredient = sample_ingredient(recipe)

        payload = {
            'name': 'Pollo a la Brasa',
            'description': 'Pollo a la Brasa',
            'ingredients': [{'name': 'Pollo'}, {'name': 'Papas'}]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload, 'json')

        old_ingredients = IngredientSerializer(ingredient)
        ingredients = Ingredient.objects.all()
        all_ingredients = IngredientSerializer(ingredients, many=True)

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertNotIn(old_ingredients.data, all_ingredients.data)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = sample_recipe()
        sample_ingredient(recipe)
        sample_ingredient(recipe)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.all().count(), 0)
        self.assertEqual(Ingredient.objects.all().count(), 0)
