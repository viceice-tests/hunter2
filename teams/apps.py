from django.apps import AppConfig

import logging


class TeamsConfig(AppConfig):
    name = 'teams'

    def ready(self):
        logging.error('Init bruv')
        super(TeamsConfig, self).ready()
        from . import signals
