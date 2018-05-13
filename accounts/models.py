from django.contrib.auth.models import User
from django.db import models

import events.models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.user.username

    def attendance_at(self, event):
        attendance, created = self.attendance_set.get_or_create(event=event)
        return attendance

    def is_on_explicit_team(self, event):
        return self.teams.filter(at_event=event).exclude(name='').exists()

    def team_at(self, event):
        return self.teams.get(at_event=event)


class Attendance(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE)
    seat = models.CharField(
        max_length=12,
        blank=True,
        default='',
        help_text='Enter your seat so we can find you easily if you get stuck. (To help you, not to mock you <3)'
    )
