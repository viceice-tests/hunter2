from django.contrib.postgres.fields import JSONField
from django.db import models
from events.models import Event
from sortedm2m.fields import SortedManyToManyField
from . import runtime as rt

import teams


class Puzzle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    runtime = models.CharField(
        max_length=1, choices=rt.RUNTIMES, default=rt.STATIC
    )
    content = models.TextField()
    cb_runtime = models.CharField(
        max_length=1, choices=rt.RUNTIMES, default=rt.STATIC
    )
    cb_content = models.TextField(blank=True, default='')

    def __str__(self):
        return '<Puzzle: {}>'.format(self.title)

    def unlocked_by(self, team):
        episode = self.episodes.get(event=team.at_event)
        return episode.unlocked_by(team) and \
            episode._puzzle_unlocked_by(self, team)

    def answered_by(self, team):
        guesses = Guess.objects.filter(
            by__in=team.users.all()
        ).filter(
            for_puzzle=self
        )
        return any([guess.is_right() for guess in guesses])


class Episode(models.Model):
    puzzles = SortedManyToManyField(
        Puzzle, blank=True, related_name='episodes'
    )
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    event = models.ForeignKey(Event, related_name='episodes')

    class Meta:
        unique_together = (('event', 'start_date'))

    def __str__(self):
        return '<Episode: {} - {}>'.format(self.event.name, self.name)

    def get_puzzle(self, puzzle_number):
        n = int(puzzle_number)
        return self.puzzles.all()[n - 1:n].get()

    def unlocked_by(self, team):
        prequels = Episode.objects.filter(
            event=self.event,
            start_date__lt=self.start_date
        )
        return all([episode.finished_by(team) for episode in prequels])

    def finished_by(self, team):
        return all([puzzle.answered_by(team) for puzzle in self.puzzles])

    def _puzzle_unlocked_by(self, puzzle, team):
        for p in self.puzzles.all():
            if p == puzzle:
                return True
            if not p.answered_by(team):
                return False


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
    runtime = models.CharField(
        max_length=1, choices=rt.RUNTIMES, default=rt.STATIC
    )
    guess = models.TextField()

    def validate_guess(self, guess):
        return rt.runtime_validate[self.runtime](
            self.answer, {'guess': guess}
        )


class Answer(models.Model):
    for_puzzle = models.ForeignKey(Puzzle, related_name='answers')
    runtime = models.CharField(
        max_length=1, choices=rt.RUNTIMES, default=rt.STATIC
    )
    answer = models.TextField()

    def __str__(self):
        return '<Answer: {}>'.format(self.answer)

    def validate_guess(self, guess):
        return rt.runtime_validate[self.runtime](
            self.answer, {'guess': guess}
        )


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
        for answer in self.for_puzzle.answers.all():
            if answer.validate_guess(self.guess):
                return True
        return False


class TeamPuzzleData(models.Model):
    puzzle = models.ForeignKey(Puzzle, related_name='teamdata')
    team = models.ForeignKey(teams.models.Team)
    data = JSONField(default={})

    class Meta:
        verbose_name_plural = 'Team puzzle data'

    def __str__(self):
        return '<TeamPuzzleData: {} - {}>'.format(
            self.team.name, self.puzzle.title
        )


class UserPuzzleData(models.Model):
    puzzle = models.ForeignKey(Puzzle, related_name='userdata')
    user = models.ForeignKey(teams.models.UserProfile)
    data = JSONField(default={})

    class Meta:
        verbose_name_plural = 'User puzzle data'

    def __str__(self):
        return '<UserPuzzleData: {} - {}>'.format(
            self.user.name, self.puzzle.title
        )
