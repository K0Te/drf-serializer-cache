from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'tests.app'
    label = 'test-app'
    verbose_name = 'Test Application'
