from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import events


@python_2_unicode_compatible
class Team(models.Model):
    class Meta:
        unique_together = (('name', 'at_event'), )

    name = models.CharField(max_length=100)
    at_event = models.ForeignKey(events.models.Event, related_name='teams')
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return '<Team: {} @{}>'.format(self.name, self.at_event.name)

    def add_user(self, user):
        user.team = self
        user.save()

    def clean(self):
        if (
            self.is_admin and
            Team.objects.exclude(
                id=self.id
            ).filter(
                at_event=self.at_event
            ).filter(
                is_admin=True
            ).count() > 0
        ):
            raise ValidationError('There can only be one admin team per event')


@python_2_unicode_compatible
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    teams = models.ManyToManyField(Team, blank=True, related_name='users')

    def __str__(self):
        return '<UserProfile: {}>'.format(self.user.username)

    def team_at(self, event):
        return self.teams.get(at_event=event)
