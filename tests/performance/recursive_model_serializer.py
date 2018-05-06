import os
import django
import timeit


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'  # noqa
django.setup()  # noqa

from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework import fields
from tests.app import models
from tests.app.serializers import CategoryHierarchySerializer as CachedHierarchy
from django.db import connection


class UserSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'name')


class FilmCategorySerializer(ModelSerializer):
    class Meta:
        model = models.FilmCategory
        fields = ('id', 'name')


class FilmSerializer(ModelSerializer):
    uploaded_by = UserSerializer()
    category = FilmCategorySerializer()

    class Meta:
        model = models.Film
        fields = ('id', 'name', 'category', 'year', 'uploaded_by')


class CategoryHierarchySerializer(Serializer):
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

def main():
    user = models.User.objects.create(name='Bob')
    top_category = models.FilmCategory.objects.create(name='All')
    child_movies = models.FilmCategory.objects.create(
        name='Child movies', parent_category=top_category)
    cartoons = models.FilmCategory.objects.create(
        name='Cartoons', parent_category=child_movies)
    serious_stuff = models.FilmCategory.objects.create(
        name='Serious', parent_category=top_category)
    anime = models.FilmCategory.objects.create(
        name='Anime', parent_category=serious_stuff)
    object = models.CategoryHierarchy(
        top_category,
        categories=[
            models.CategoryHierarchy(
                child_movies,
                categories=[
                    models.CategoryHierarchy(
                        cartoons,
                        films=[
                            models.Film.objects.create(name='Mickey Mouse',
                                                       year=1966,
                                                       uploaded_by=user,
                                                       category=cartoons)
                            for _ in range(10)
                        ]
                    )
                ]
            ),
            models.CategoryHierarchy(
                serious_stuff,
                categories=[
                    models.CategoryHierarchy(
                        anime,
                        films=[
                            models.Film.objects.create(name='Ghost in the shell',
                                                       year=1989,
                                                       uploaded_by=user,
                                                       category=anime)
                            for _ in range(10)
                        ]
                    )
                ]
            ),
        ])

    def simple_serialize():
        return CategoryHierarchySerializer(object).data

    def cached_serialize():
        return CachedHierarchy(object).data

    assert simple_serialize() == cached_serialize(), 'Result is wrong'
    print('Model with recursion serializer: ',
          timeit.timeit('simple_serialize()',
                        globals={'simple_serialize': simple_serialize},
                        number=500))
    print('Cached model with recursion serializer: ',
          timeit.timeit('cached_serialize()',
                        globals={'cached_serialize': cached_serialize},
                        number=500))


if __name__ == '__main__':
    connection.creation.create_test_db()
    main()
    connection.creation.destroy_test_db()
