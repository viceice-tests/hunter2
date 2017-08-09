from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = 'events'

    def ready(self):
        super(EventsConfig, self).ready()
        from . import signals  # noqa: F401
