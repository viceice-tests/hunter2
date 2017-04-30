from django.apps import AppConfig


class TeamsConfig(AppConfig):
    name = 'teams'

    def ready(self):
        super(TeamsConfig, self).ready()
        from . import signals
