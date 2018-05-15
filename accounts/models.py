from django.contrib.auth.models import User
from django.db import models


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
