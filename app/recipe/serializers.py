from rest_framework import serializers

from core.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""
    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serialize a recipe"""
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'ingredients', 'description'
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        new_ingredients = validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(**validated_data)

        for new_ingredient in new_ingredients:
            Ingredient.objects.create(recipe=new_recipe,
                                      name=new_ingredient['name'])

        return new_recipe

    def update(self, instance, validated_data):
        new_ingredients = validated_data.pop('ingredients', [])
        if len(new_ingredients) > 0:
            instance.ingredients.all().delete()
            for new_ingredient in new_ingredients:
                Ingredient.objects.create(recipe=instance,
                                          name=new_ingredient['name'])

        super().update(instance, validated_data)

        return instance
