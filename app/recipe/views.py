from rest_framework import viewsets
from core.models import Recipe

from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve the recipes"""
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__contains=name)

        return queryset.order_by('-id')

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save()
