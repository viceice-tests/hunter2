from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

import events


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    seat = models.CharField(
        max_length=12,
        blank=True,
        default='',
        help_text='Enter your seat so we can find you easily if you get stuck. (To help you, not to mock you <3)'
    )

    def __str__(self):
        return f'<UserProfile: {self.user.username}>'

    def is_on_explicit_team(self, event):
        return self.teams.filter(at_event=event).exclude(name='').exists()

    def team_at(self, event):
        return self.teams.get(at_event=event)


class Team(models.Model):
    name = models.CharField(blank=True, max_length=100)
    at_event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE, related_name='teams')
    is_admin = models.BooleanField(default=False)
    members = models.ManyToManyField(UserProfile, blank=True, related_name='teams')
    invites = models.ManyToManyField(UserProfile, blank=True, related_name='team_invites')
    requests = models.ManyToManyField(UserProfile, blank=True, related_name='team_requests')

    def __str__(self):
        return f'<Team: {self.name} @{self.at_event.name}>'

    def clean(self):
        if (
            self.is_admin and
            Team.objects.exclude(id=self.id).filter(at_event=self.at_event).filter(is_admin=True).count() > 0
        ):
            raise ValidationError('There can only be one admin team per event')

    def save(self):
        if self.name != '':
            conflicts = Team.objects.filter(name=self.name, at_event=self.at_event)
            conflicts = conflicts.exclude(pk=self.id)
            if conflicts.exists():
                raise ValidationError('Cannot have multiple teams with the same non-empty name at an event')
        return super().save()

    def get_absolute_url(self):
        return reverse('team', args=[self.pk])

    def is_full(self):
        return self.members.count() >= self.at_event.max_team_size > 0
