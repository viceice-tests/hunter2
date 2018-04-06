from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator
from django_tenants.models import TenantMixin, DomainMixin

from .fields import SingleTrueBooleanField


class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    script = models.TextField(blank=True)
    style = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Tenant(TenantMixin):
    pass


class Domain(DomainMixin):
    pass


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='theme')
    current = SingleTrueBooleanField()
    about_text = models.TextField(help_text='Content for the event about page')
    rules_text = models.TextField(help_text='Content for the event rules page')
    help_text = models.TextField(help_text='Content for the event help page')
    examples_text = models.TextField(help_text='Content for the example puzzles for this event')
    max_team_size = models.IntegerField(default=0, help_text="Maximum size for a team at this event, or 0 for no limit.", validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    def clean(self):
        if (
            self.current and
            Event.objects.exclude(id=self.id).filter(current=True).count() > 0
        ):
            raise ValidationError('There can only be one current event')


def event_file_path(instance, filename):
    return 'events/{0}/{1}'.format(instance.event.id, filename)


class EventFile(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    slug = models.SlugField()
    file = models.FileField(upload_to=event_file_path)

    class Meta:
        unique_together = (('event', 'slug'), )
