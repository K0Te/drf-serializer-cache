import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'  # noqa
django.setup()  # noqa

from collections import namedtuple
from rest_framework.serializers import Serializer
from rest_framework import fields
from drf_serializer_cache import SerializerCacheMixin


class PointSerializer(SerializerCacheMixin, Serializer):
    x = fields.IntegerField()
    y = fields.IntegerField(source='xx')


def test_single_point():
    serializer = PointSerializer({'x': 1, 'xx': 123})
    assert serializer.data['x'] == 1
    assert serializer.data['y'] == 123


def test_point_list():
    serializer = PointSerializer([{'x': 1, 'xx': 123},
                                  {'x': 123, 'xx': 456}],
                                 many=True)
    assert serializer.data[0]['x'] == 1
    assert serializer.data[0]['y'] == 123
    assert serializer.data[1]['x'] == 123
    assert serializer.data[1]['y'] == 456


def test_point_same_element():
    class CountedSerializer(Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_count = 0

        def to_representation(self, instance):
            self.call_count += 1
            res = super().to_representation(instance)
            res.update({'count': self.call_count})
            return res

    class CountedPointSerializer(CountedSerializer):
        x = fields.IntegerField()
        y = fields.IntegerField()

    class CachedCountedPointSerializer(SerializerCacheMixin, CountedSerializer):
        x = fields.IntegerField()
        y = fields.IntegerField()

    point_cls = namedtuple('Point', 'x y')
    p1 = point_cls(1, 2)
    p2 = point_cls(3, 4)

    serializer = CountedPointSerializer([p1, p2, p1, p2], many=True)
    assert serializer.data[0]['x'] == 1
    assert serializer.data[0]['y'] == 2
    assert serializer.data[0]['count'] == 1
    assert serializer.data[-1]['x'] == 3
    assert serializer.data[-1]['y'] == 4
    # non-cached variant yields 4
    assert serializer.data[-1]['count'] == 4

    serializer = CachedCountedPointSerializer([p1, p2, p1, p2], many=True)
    assert serializer.data[0]['x'] == 1
    assert serializer.data[0]['y'] == 2
    assert serializer.data[0]['count'] == 1
    assert serializer.data[-1]['x'] == 3
    assert serializer.data[-1]['y'] == 4
    # cached variant yields 2 - as there are two distinct objects
    assert serializer.data[-1]['count'] == 2


def test_root_non_cachable():
    class RootSerializer(Serializer):
        points = PointSerializer(many=True)

    serializer = RootSerializer(
        {'points': [{'x': 1, 'xx': 123}, {'x': 123, 'xx': 456}]})
    assert serializer.data['points'][0]['x'] == 1
    assert serializer.data['points'][0]['y'] == 123
    assert serializer.data['points'][1]['x'] == 123
    assert serializer.data['points'][1]['y'] == 456


def test_validate_serializer():
    p = PointSerializer(data={'x': 1, 'y': 123})
    p.is_valid(raise_exception=True)

    data = p.validated_data
    assert data['x'] == 1
    assert data['xx'] == 123
