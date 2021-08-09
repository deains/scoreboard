from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'score'
    verbose_name = 'score'

    def ready(self):
        from . import hardware  # noqa
