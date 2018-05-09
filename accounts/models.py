from django.contrib.auth.models import User
from django.db import models


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
