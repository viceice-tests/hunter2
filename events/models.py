from django.core.exceptions import ValidationError
from django.db import models
from hunts.models import Episode, Puzzle
from django.http import Http404


class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    script = models.TextField(blank=True)
    style = models.TextField(blank=True)

    def __str__(self):
        return f'<Theme: {self.name}>'


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='theme')
    current = models.BooleanField(default=False)

    def __str__(self):
        return f'<Event: {self.name}>'

    def clean(self):
        if (
            self.current and
            Event.objects.exclude(id=self.id).filter(current=True).count() > 0
        ):
            raise ValidationError('There can only be one current event')

    def get_episode_from_relative_id(self, episode_number):
        episodes = self.episode_set.order_by('start_date')
        ep_int = int(episode_number)
        try:
            return episodes[ep_int - 1:ep_int].get()
        except Episode.DoesNotExist as e:
            raise Http404 from e

    def get_episode_and_puzzle_from_relative_id(
        self,
        episode_number,
        puzzle_number
    ):
        episode = self.get_episode_from_relative_id(episode_number)
        try:
            return episode, episode.get_puzzle(puzzle_number)
        except Puzzle.DoesNotExist as e:
            raise Http404 from e
