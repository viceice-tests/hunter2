from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import models
from hunter2.resolvers import reverse

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
        if self.seat:
            return f'{self.user.username} @{self.seat}'
        else:
            return f'{self.user.username}'

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
        return f'{self.verbose_name} @{self.at_event.name}'

    @property
    def verbose_name(self):
        if self.is_explicit():
            return self.name
        try:
            member = self.members.get()
            return f'[{member}\'s team]'
        except MultipleObjectsReturned:
            # This should never happen but we don't want things to break if it does!
            return '[anonymous team with %d members!]' % self.members.count()
        except UserProfile.DoesNotExist:
            return '[empty anonymous team]'

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
        return reverse('team', subdomain='www', kwargs={'event_id': self.at_event.pk, 'team_id': self.pk})

    def is_explicit(self):
        return self.name != ''

    def is_full(self):
        return self.members.count() >= self.at_event.max_team_size > 0 and not self.is_admin
