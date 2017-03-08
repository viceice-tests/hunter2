from django.core.exceptions import ValidationError
from django.db import models


class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    script = models.TextField(blank=True)
    style = models.TextField(blank=True)

    def __str__(self):
        return '<Theme: {}>'.format(self.name)


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    theme = models.ForeignKey(Theme, related_name='theme')
    current = models.BooleanField(default=False)

    def __str__(self):
        return '<Event: {}>'.format(self.name)

    def clean(self):
        if (
            self.current and
            Event.objects.exclude(id=self.id).filter(current=True).count() > 0
        ):
            raise ValidationError('There can only be one current event')
