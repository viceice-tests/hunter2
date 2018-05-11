from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

import accounts
import events


class Team(models.Model):
    name = models.CharField(blank=True, max_length=100)
    at_event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE, related_name='teams')
    is_admin = models.BooleanField(default=False)
    members = models.ManyToManyField(accounts.models.UserProfile, blank=True, related_name='teams')
    invites = models.ManyToManyField(accounts.models.UserProfile, blank=True, related_name='team_invites')
    requests = models.ManyToManyField(accounts.models.UserProfile, blank=True, related_name='team_requests')

    def __str__(self):
        return '%s @%s' % (self.get_verbose_name(), self.at_event)

    def get_verbose_name(self):
        if self.is_explicit():
            return self.name
        if self.members.all().count() == 1:
            # We use .all()[0] to allow for prefetch_related
            return '[%s\'s team]' % (self.members.all()[0])
        elif self.members.all().count() == 0:
            return '[empty anonymous team]'
        else:
            # This should never happen but we don't want things to break if it does!
            return '[anonymous team with %d members!]' % self.members.count()

    def clean(self):
        if (
            self.is_admin and
            Team.objects.exclude(id=self.id).filter(at_event=self.at_event).filter(is_admin=True).count() > 0
        ):
            raise ValidationError('There can only be one admin team per event')

    def save(self, *args, **kwargs):
        if self.name != '':
            conflicts = Team.objects.filter(name=self.name, at_event=self.at_event)
            conflicts = conflicts.exclude(pk=self.id)
            if conflicts.exists():
                raise ValidationError('Cannot have multiple teams with the same non-empty name at an event')
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('team', kwargs={'event_id': self.at_event.pk, 'team_id': self.pk})

    def is_explicit(self):
        return self.name != ''

    def is_full(self):
        return self.members.count() >= self.at_event.max_team_size > 0 and not self.is_admin
