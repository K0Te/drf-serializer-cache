import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'  # noqa
django.setup()  # noqa

from rest_framework.serializers import ModelSerializer
import pytest
from drf_serializer_cache import SerializerCacheMixin
from ..app import models


class UserSerializer(SerializerCacheMixin, ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'name')


@pytest.mark.django_db
def test_simple_saved():
    user = models.User.objects.create(name='Bob')
    user.save()

    serializer = UserSerializer(instance=user)
    data = serializer.data
    assert data['name'] == 'Bob'
    assert data['id'] > 0


def test_simple_unsaved():
    user = models.User(name='Bob')
    serializer = UserSerializer(instance=user)
    data = serializer.data
    assert data['name'] == 'Bob'
    assert data['id'] is None
