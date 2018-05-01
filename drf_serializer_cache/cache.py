from contextlib import contextmanager

from django.utils.functional import cached_property
from rest_framework.serializers import ListSerializer


class SerializerCacheMixin:
    """Mixin for DRF serializer performance improvement.

    Provides cache for slow "fields" property."""

    @cached_property
    def _is_first_cachable(self):
        parent = self.parent
        while parent is not None:
            if isinstance(parent, SerializerCacheMixin):
                return False
            parent = parent.parent
        return True

    @contextmanager
    def _setup_cache(self):
        assert not hasattr(self.root, '_field_cache'), \
            'Double cache setup detected.'
        self.root._field_cache = {}
        assert not hasattr(self.root, '_representation_cache'), \
            'Double cache setup detected.'
        self.root._representation_cache = {}
        yield
        del self.root._field_cache
        del self.root._representation_cache

    def to_representation(self, instance):
        """Convert instance to representation with result caching."""
        if self._is_first_cachable:
            with self._setup_cache():
                return super().to_representation(instance)
        cache = self.root._representation_cache
        key = (instance, self.__class__)
        try:
            if key not in cache:
                cache[key] = super().to_representation(instance)
            return cache[key]
        # key might not be hashable
        except TypeError:
            return super().to_representation(instance)

    @property
    def fields(self):
        """Return cached fields."""
        try:
            cache = self.root._field_cache
        except AttributeError:
            return super().fields
        if self.__class__ not in cache:
            cache[self.__class__] = super().fields
        return cache[self.__class__]


class CachedListSerializer(SerializerCacheMixin, ListSerializer):
    pass


SerializerCacheMixin.Meta = type(
    'Meta', tuple(), {'list_serializer_class': CachedListSerializer})
