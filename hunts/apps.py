from django.apps import AppConfig


class HuntsConfig(AppConfig):
    name = 'hunts'

    def ready(self):
        super(HuntsConfig, self).ready()
        from . import signals  # noqa: F401
