from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator

from .fields import SingleTrueBooleanField


class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    script = models.TextField(blank=True)
    style = models.TextField(blank=True)

    def __str__(self):
        return f'<Theme: {self.name}>'


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='theme')
    current = SingleTrueBooleanField()
    max_team_size = models.IntegerField(default=0, help_text="Maximum size for a team at this event, or 0 for no limit.", validators=[MinValueValidator(0)])

    def __str__(self):
        return f'<Event: {self.name}>'

    def clean(self):
        if (
            self.current and
            Event.objects.exclude(id=self.id).filter(current=True).count() > 0
        ):
            raise ValidationError('There can only be one current event')
