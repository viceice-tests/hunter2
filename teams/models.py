from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import events


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f'<UserProfile: {self.user.username}>'

    def team_at(self, event):
        return self.teams.get(at_event=event)


class Team(models.Model):
    name = models.CharField(max_length=100)
    at_event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE, related_name='teams')
    is_admin = models.BooleanField(default=False)
    members = models.ManyToManyField(UserProfile, blank=True, related_name='teams')
    invites = models.ManyToManyField(UserProfile, blank=True, related_name='team_invites')
    requests = models.ManyToManyField(UserProfile, blank=True, related_name='team_requests')

    class Meta:
        unique_together = (('name', 'at_event'), )

    def __str__(self):
        return f'<Team: {self.name} @{self.at_event.name}>'

    def clean(self):
        if (
            self.is_admin and
            Team.objects.exclude(id=self.id).filter(at_event=self.at_event).filter(is_admin=True).count() > 0
        ):
            raise ValidationError('There can only be one admin team per event')
