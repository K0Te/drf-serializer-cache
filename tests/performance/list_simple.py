import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'  # noqa
django.setup()  # noqa

from rest_framework.serializers import Serializer
from rest_framework import fields

from drf_serializer_cache import SerializerCacheMixin


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


points = [Point(x, y, z)
          for x in range(10)
          for y in range(10)
          for z in range(10)]


class PointSerializer(Serializer):
    x = fields.IntegerField()
    y = fields.IntegerField()
    z = fields.IntegerField()


class CachedPointSerializer(SerializerCacheMixin, PointSerializer):
    pass


def simple_serialize():
    return PointSerializer(points, many=True).data


def cached_serialize():
    return CachedPointSerializer(points, many=True).data


if __name__ == '__main__':
    import timeit
    assert simple_serialize() == cached_serialize(), 'Result is wrong'
    print('Simple list serializer without cache: ',
          timeit.timeit('simple_serialize()',
                        setup='from __main__ import simple_serialize',
                        number=100))
    print('Simple list serializer with cache(100% cache miss): ',
          timeit.timeit('cached_serialize()',
                        setup='from __main__ import cached_serialize',
                        number=100))
