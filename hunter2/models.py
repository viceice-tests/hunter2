from django.db import models
from solo.models import SingletonModel

class Configuration(SingletonModel):
    index_content = models.TextField()
