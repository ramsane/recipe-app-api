from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # function that overriddes the get_querysets
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    # since this requites an authentication, we add this
    authentication_classes = (TokenAuthentication, )
    # add permission classes as this requires permission
    permission_classes = (IsAuthenticated,)
    # add query sets that this viewset has to handle
    queryset = Ingredient.objects.all()
    # mention the serializer for this viewset
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """create a new Ingredient"""
        serializer.save(user=self.request.user)
