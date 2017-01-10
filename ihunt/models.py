from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField
from time import strftime

import events
import teams


@python_2_unicode_compatible
class Puzzle(models.Model):
    title = models.TextField(unique=True)
    content = models.TextField()

    def __str__(self):
        return '<Puzzle: {}>'.format(self.title)


@python_2_unicode_compatible
class Episode(models.Model):
    puzzles = SortedManyToManyField(Puzzle, blank=True)
    start_date = models.DateTimeField()
    event = models.ForeignKey(events.models.Event, related_name='episodes')

    def __str__(self):
        return '<Episode: {} - {}>'.format(
            self.event.name, strftime('%A %H:%M', self.start_date.timetuple())
        )


class Clue(models.Model):
    puzzle = models.ForeignKey(Puzzle)
    text = models.TextField()

    class Meta:
        abstract = True


class Hint(Clue):
    time = models.DurationField()


class Unlock(Clue):
    pass


class UnlockGuess(models.Model):
    unlock = models.ForeignKey(Unlock, related_name='guess')
    guess = models.TextField()


@python_2_unicode_compatible
class Answer(models.Model):
    for_puzzle = models.ForeignKey(Puzzle, related_name='answers')
    answer = models.TextField()

    def __str__(self):
        return '<Answer: {}>'.format(self.answer)


@python_2_unicode_compatible
class Guess(models.Model):
    for_puzzle = models.ForeignKey(Puzzle)
    by = models.ForeignKey(teams.models.UserProfile)
    guess = models.TextField()
    given = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Guesses'

    def __str__(self):
        return '<Guess: {} by {}>'.format(
            self.guess, self.by.user.username
        )

    def is_right(self):
        for answer in self.for_puzzle.Answer_set:
            if answer == self.guess:
                return True
        return False


class TeamPuzzleData(models.Model):
    puzzle = models.ForeignKey(Puzzle)
    team = models.ForeignKey(teams.models.Team)
    data = JSONField()


class UserPuzzleData(models.Model):
    puzzle = models.ForeignKey(Puzzle)
    user = models.ForeignKey(teams.models.UserProfile)
    data = JSONField()
