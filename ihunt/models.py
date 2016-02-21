from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField
from time import strftime


@python_2_unicode_compatible
class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    script = models.TextField(blank=True)
    style = models.TextField(blank=True)

    def __str__(self):
        return '<Theme: {}>'.format(self.name)


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    theme = models.ForeignKey(Theme, related_name='theme')
    current = models.BooleanField(default=False)

    def __str__(self):
        return '<Event: {}>'.format(self.name)

    def clean(self):
        if self.current and Event.objects.filter(current=True).count() > 0:
            raise ValidationError('There can only be one current event')


@python_2_unicode_compatible
class Puzzle(models.Model):
    title = models.TextField(unique=True)
    content = models.TextField()

    def __str__(self):
        return '<Puzzle: {}>'.format(self.title)


@python_2_unicode_compatible
class PuzzleSet(models.Model):
    puzzles = SortedManyToManyField(Puzzle, blank=True)
    start_date = models.DateTimeField()
    event = models.ForeignKey(Event, related_name='puzzlesets')

    def __str__(self):
        return '<PuzzleSet: {} - {}>'.format(
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
class Team(models.Model):
    class Meta:
        unique_together = (('name', 'at_event'), )

    name = models.CharField(max_length=100)
    at_event = models.ForeignKey(Event, related_name='teams')

    def __str__(self):
        return '<Team: {} @{}>'.format(self.name, self.at_event.name)

    def add_user(self, user):
        user.team = self
        user.save()


@python_2_unicode_compatible
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    teams = models.ManyToManyField(Team, blank=True, related_name='users')

    def __str__(self):
        return '<UserProfile: {}>'.format(self.user.username)

    def team_at(self, event):
        return self.teams.get(at_event=event)


@python_2_unicode_compatible
class Guess(models.Model):
    for_puzzle = models.ForeignKey(Puzzle)
    by = models.ForeignKey(UserProfile)
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
