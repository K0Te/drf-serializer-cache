from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import fields

from drf_serializer_cache import SerializerCacheMixin
from tests.app import models


class UserSerializer(SerializerCacheMixin, ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'name')


class FilmCategorySerializer(SerializerCacheMixin, ModelSerializer):
    class Meta:
        model = models.FilmCategory
        fields = ('id', 'name')


class FilmSerializer(SerializerCacheMixin, ModelSerializer):
    uploaded_by = UserSerializer()
    category = FilmCategorySerializer()

    class Meta:
        model = models.Film
        fields = ('id', 'name', 'category', 'year', 'uploaded_by')


class CategoryHierarchySerializer(SerializerCacheMixin, Serializer):
    category = FilmCategorySerializer()
    films = fields.SerializerMethodField()
    categories = fields.SerializerMethodField()

    def get_films(self, instance):
        serializer = FilmSerializer(instance.films, many=True)
        serializer.bind('*', self)
        return serializer.data

    def get_categories(self, instance):
        serializer = self.__class__(instance.categories, many=True)
        serializer.bind('*', self)
        return serializer.data
