# vim: set fileencoding=utf-8 :
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils import timezone
from sortedm2m.fields import SortedManyToManyField
from .runtimes.registry import RuntimesRegistry as rr
from datetime import timedelta
from enumfields import EnumField, Enum
from hunter2.resolvers import reverse

import events
import teams
import uuid


class Puzzle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    flavour = models.TextField(
        blank=True, verbose_name="Flavour text",
        help_text="Separate flavour text for the puzzle. Should not be required for solving the puzzle")
    runtime = models.CharField(
        max_length=1, choices=rr.RUNTIME_CHOICES, default=rr.STATIC,
        help_text="Runtime for generating the question content"
    )
    content = models.TextField()
    cb_runtime = models.CharField(
        max_length=1, choices=rr.RUNTIME_CHOICES, default=rr.STATIC, verbose_name="Callback runtime",
        help_text="Runtime for responding to an AJAX callback for this question, should return JSON"
    )
    cb_content = models.TextField(blank=True, default='', verbose_name="Callback content")
    start_date = models.DateTimeField(blank=True, default=timezone.now)
    headstart_granted = models.DurationField(
        default=timedelta(),
        help_text='How much headstart this puzzle gives to later episodes which gain headstart from this episode'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        try:
            episode = self.episode_set.get()
        except Episode.DoesNotExist:
            return ''

        params = {
            'event_id': episode.event.pk,
            'episode_number': episode.get_relative_id(),
            'puzzle_number': self.get_relative_id()
        }
        return reverse('puzzle', subdomain='www', kwargs=params)

    def get_relative_id(self):
        try:
            episode = self.episode_set.get()
        except Episode.DoesNotExist:
            raise ValueError("Puzzle %s is not on an episode and so has no relative id" % self.title)

        for i, p in enumerate(episode.puzzles.values('pk')):
            if self.pk == p['pk']:
                puzzle_number = i + 1
                break

        return puzzle_number

    def unlocked_by(self, team):
        # Is this puzzle playable?
        # TODO: Make it not depend on a team. So single player puzzles work.
        episode = self.episode_set.get(event=team.at_event)
        return episode.unlocked_by(team) and \
            episode._puzzle_unlocked_by(self, team)

    def answered_by(self, team):
        """Return a list of correct guesses for this puzzle by the given team, ordered by when they were given."""
        # Select related since get_correct_for() will want it
        guesses = Guess.objects.filter(
            by__in=team.members.all(),
            for_puzzle=self,
        ).order_by(
            'given'
        ).select_related('correct_for')

        # TODO: Should return bool
        return [g for g in guesses if g.get_correct_for()]

    def first_correct_guesses(self, event):
        """Returns a dictionary of teams to guesses, where the guess is that team's earliest correct, validated guess for this puzzle"""
        # Select related to avoid a load of queries for answers and teams
        correct_guesses = Guess.objects.filter(
            for_puzzle=self,
        ).order_by(
            'given'
        ).select_related('correct_for', 'by_team')

        team_guesses = {}
        for g in correct_guesses:
            if g.get_correct_for() and g.by_team not in team_guesses:
                team_guesses[g.by_team] = g

        return team_guesses

    def finished_teams(self, event):
        """Return a list of teams who have completed this puzzle at the given event in order of completion."""
        team_guesses = self.first_correct_guesses(event)

        return sorted(team_guesses.keys(), key=lambda t: (team_guesses[t].given, team_guesses[t].pk))

    def position(self, team):
        """Returns the position in which the given team finished this puzzle: 0 = first, None = not yet finished."""
        try:
            return self.finished_teams(team.at_event).index(team)
        except ValueError:
            return None


def puzzle_file_path(instance, filename):
    return 'puzzles/{0}/{1}'.format(instance.puzzle.id, filename)


class PuzzleFile(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    slug = models.SlugField(help_text="Include the URL of the file in puzzle content using $slug or ${slug}.")
    file = models.FileField(upload_to=puzzle_file_path)

    class Meta:
        unique_together = (('puzzle', 'slug'), )


class Clue(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    text = models.TextField(help_text="Text displayed when this clue is unlocked")

    class Meta:
        abstract = True


class Hint(Clue):
    time = models.DurationField()

    def __str__(self):
        return f'Hint unlocked after {self.time}'

    def unlocked_by(self, team, data):
        if data.tp_data.start_time:
            return data.tp_data.start_time + self.time < timezone.now()
        else:
            return False


class Unlock(Clue):
    def unlocked_by(self, team):
        guesses = Guess.objects.filter(
            by__in=team.members.all()
        ).filter(
            for_puzzle=self.puzzle
        )
        return [g for g in guesses if any([u.validate_guess(g) for u in self.unlockanswer_set.all()])]

    def __str__(self):
        return f'Unlock for {self.puzzle}'


class UnlockAnswer(models.Model):
    unlock = models.ForeignKey(Unlock, on_delete=models.CASCADE)
    runtime = models.CharField(
        max_length=1, choices=rr.RUNTIME_CHOICES, default=rr.STATIC
    )
    guess = models.TextField()

    def __str__(self):
        if self.runtime == rr.STATIC or self.runtime == rr.REGEX:
            return self.guess
        else:
            return '[Using %s]' % self.get_runtime_display()

    def validate_guess(self, guess):
        return rr.validate_guess(
            self.runtime,
            self.guess,
            guess.guess,
        )


class Answer(models.Model):
    for_puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    runtime = models.CharField(
        max_length=1, choices=rr.RUNTIME_CHOICES, default=rr.STATIC
    )
    answer = models.TextField()

    def __str__(self):
        if self.runtime == rr.STATIC or self.runtime == rr.REGEX:
            return self.answer
        else:
            return '[Using %s]' % self.get_runtime_display()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        guesses = Guess.objects.filter(
            Q(for_puzzle=self.for_puzzle),
            Q(correct_for__isnull=True) | Q(correct_for=self)
        )
        guesses.update(correct_current=False)

    def delete(self, *args, **kwargs):
        guesses = Guess.objects.filter(
            for_puzzle=self.for_puzzle,
            correct_for=self
        )
        guesses.update(correct_current=False)
        super().delete(*args, **kwargs)

    def validate_guess(self, guess):
        return rr.validate_guess(
            self.runtime,
            self.answer,
            guess.guess,
        )


class Guess(models.Model):
    for_puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    by = models.ForeignKey(teams.models.UserProfile, on_delete=models.CASCADE)
    by_team = models.ForeignKey(teams.models.Team, on_delete=models.PROTECT)
    guess = models.TextField()
    given = models.DateTimeField(auto_now_add=True)
    # The following two fields cache whether the guess is correct. Do not use them directly.
    correct_for = models.ForeignKey(Answer, blank=True, null=True, on_delete=models.SET_NULL)
    correct_current = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Guesses'

    def __str__(self):
        return f'"{self.guess}" by {self.by} ({self.by_team})'

    def get_team(self):
        event = self.for_puzzle.episode_set.get().event
        return teams.models.Team.objects.filter(at_event=event, members=self.by).get()

    def get_correct_for(self):
        """Get the first answer this guess is correct for, if such exists."""
        if not self.correct_current:
            self._evaluate_correctness()
            self.save(update_team=False)

        return self.correct_for

    def _evaluate_correctness(self, data=None, answers=None):
        """Re-evaluate self.correct_current and self.correct_for.

        Sets self.correct_current to True, and self.correct_for to the first
        answer this is correct for, if such exists. Does not save the model."""
        if data is None:
            data = PuzzleData(self.for_puzzle, self.by_team)
        if answers is None:
            answers = self.for_puzzle.answer_set.all()

        self.correct_for = None
        self.correct_current = True

        for answer in answers:
            if answer.validate_guess(self):
                self.correct_for = answer
                return

    def save(self, *args, update_team=True, **kwargs):
        if update_team:
            self.by_team = self.get_team()
        self._evaluate_correctness()
        super().save(*args, **kwargs)

    def time_on_puzzle(self):
        data = TeamPuzzleData.objects.filter(
            puzzle=self.for_puzzle,
            team=self.by_team
        ).get()
        if not data.start_time:
            # This should never happen, but can do with sample data.
            return '0'
        time_active = self.given - data.start_time
        hours, seconds = divmod(time_active.total_seconds(), 3600)
        minutes, seconds = divmod(seconds, 60)
        return '%02d:%02d:%02d' % (hours, minutes, seconds)


class TeamData(models.Model):
    team = models.ForeignKey(teams.models.Team, on_delete=models.CASCADE)
    data = JSONField(default={})

    class Meta:
        verbose_name_plural = 'Team data'

    def __str__(self):
        return f'Data for {self.team.name}'


class UserData(models.Model):
    event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE)
    user = models.ForeignKey(teams.models.UserProfile, on_delete=models.CASCADE)
    data = JSONField(default={})

    class Meta:
        verbose_name_plural = 'User data'

    def __str__(self):
        return f'Data for {self.user.user.username} at {self.event}'


class TeamPuzzleData(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    team = models.ForeignKey(teams.models.Team, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    data = JSONField(default={})

    class Meta:
        verbose_name_plural = 'Team puzzle data'

    def __str__(self):
        return f'Data for {self.team.name} on {self.puzzle.title}'


class UserPuzzleData(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    user = models.ForeignKey(teams.models.UserProfile, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    data = JSONField(default={})

    class Meta:
        verbose_name_plural = 'User puzzle data'

    def __str__(self):
        return f'Data for {self.user.user.username} on {self.puzzle.title}'

    def team(self):
        """Helper method to fetch the team associated with this user and puzzle"""
        event = self.puzzle.episode_set.get().event
        return self.user.team_at(event)


# Convenience class for using all the above data objects together
class PuzzleData:
    from .models import TeamData, UserData, TeamPuzzleData, UserPuzzleData

    def __init__(self, puzzle, team, user=None):
        self.t_data, created = TeamData.objects.get_or_create(team=team)
        self.tp_data, created = TeamPuzzleData.objects.get_or_create(
            puzzle=puzzle, team=team
        )
        if user:
            self.u_data, created = UserData.objects.get_or_create(
                event=team.at_event, user=user
            )
            self.up_data, created = UserPuzzleData.objects.get_or_create(
                puzzle=puzzle, user=user
            )

    def save(self):
        self.t_data.save()
        self.tp_data.save()
        if self.u_data:
            self.u_data.save()
        if self.up_data:
            self.up_data.save()


class Episode(models.Model):
    name = models.CharField(max_length=255)
    flavour = models.TextField(blank=True)
    puzzles = SortedManyToManyField(Puzzle, blank=True)
    prequels = models.ManyToManyField(
        'self', blank=True,
        help_text='Set of episodes which must be completed before starting this one', related_name='sequels',
        symmetrical=False,
    )
    start_date = models.DateTimeField()
    event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE)
    parallel = models.BooleanField(default=False)
    headstart_from = models.ManyToManyField(
        "self", blank=True,
        help_text='Episodes which should grant a headstart for this episode',
        symmetrical=False,
    )

    class Meta:
        unique_together = (('event', 'start_date'),)

    def __str__(self):
        return f'{self.event.name} - {self.name}'

    def follows(self, episode):
        """Does this episode follow the provied episode by one or more prequel relationships?"""
        if episode in self.prequels.all():
            return True
        else:
            return any([p.follows(episode) for p in self.prequels.all()])

    def get_puzzle(self, puzzle_number):
        n = int(puzzle_number)
        return self.puzzles.all()[n - 1:n].get()

    def next_puzzle(self, team):
        """return the relative id of the next puzzle the player should attempt, or None.

        None is returned if the puzzle is parallel and there is not exactly
        one unlocked puzzle, or if it is linear and all puzzles have been unlocked."""

        if self.parallel:
            unlocked = None
            for i, puzzle in enumerate(self.puzzles.all()):
                if not puzzle.answered_by(team):
                    if unlocked is None:
                        unlocked = i + 1
                    else:
                        return None
            return unlocked
        else:
            for i, puzzle in enumerate(self.puzzles.all()):
                if not puzzle.answered_by(team):
                    return i + 1

        return None

    def started(self, team=None):
        date = self.start_date
        if team:
            date -= self.headstart_applied(team)

        return date < timezone.now()

    def get_relative_id(self):
        episodes = self.event.episode_set.order_by('start_date')
        for index, e in enumerate(episodes):
            if e == self:
                return index + 1
        return -1

    def unlocked_by(self, team):
        return all([episode.finished_by(team) for episode in self.prequels.all()])

    def finished_by(self, team):
        return all([puzzle.answered_by(team) for puzzle in self.puzzles.all()])

    def finished_positions(self):
        """Get a list of teams who have finished this episode in order of finishing."""
        if not self.puzzles.all():
            return []

        if self.parallel:
            # The position is determined by when the latest of a team's first successful guesses came in, over
            # all puzzles in the episode. Teams which haven't answered all questions are discarded.
            last_team_guesses = {team: None for team in teams.models.Team.objects.filter(at_event=self.event)}

            for p in self.puzzles.all():
                team_guesses = p.first_correct_guesses(self.event)
                for team in list(last_team_guesses.keys()):
                    if team not in team_guesses:
                        del last_team_guesses[team]
                        continue
                    if not last_team_guesses[team]:
                        last_team_guesses[team] = team_guesses[team]
                    elif team_guesses[team].given > last_team_guesses[team].given:
                        last_team_guesses[team] = team_guesses[team]

            return sorted(last_team_guesses.keys(), key=lambda t: last_team_guesses[t].given)

        else:
            last_puzzle = self.puzzles.all().last()
            return last_puzzle.finished_teams(self.event)

    def headstart_applied(self, team):
        """The headstart that the team has acquired that will be applied to this episode"""
        seconds = sum([e.headstart_granted(team).total_seconds() for e in self.headstart_from.all()])
        return timedelta(seconds=seconds)

    def headstart_granted(self, team):
        """The headstart that the team has acquired by completing puzzles in this episode"""
        seconds = sum([p.headstart_granted.total_seconds() for p in self.puzzles.all() if p.answered_by(team)])
        return timedelta(seconds=seconds)

    def _puzzle_unlocked_by(self, puzzle, team):
        started_puzzles = self.puzzles.filter(start_date__lt=timezone.now())
        if self.parallel:
            return puzzle in started_puzzles
        else:
            for p in started_puzzles:
                if p == puzzle:
                    return True
                if not p.answered_by(team):
                    return False

    def unlocked_puzzles(self, team):
        started_puzzles = self.puzzles.filter(start_date__lt=timezone.now())
        if self.parallel:
            return started_puzzles
        else:
            result = []
            for p in started_puzzles:
                result.append(p)
                if not p.answered_by(team):
                    break

            return result


class AnnouncementType(Enum):
    INFO = 'I'
    SUCCESS = 'S'
    WARNING = 'W'
    ERROR = 'E'


class Announcement(models.Model):
    event = models.ForeignKey(events.models.Event, on_delete=models.CASCADE, related_name='announcements')
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    title = models.CharField(max_length=255)
    posted = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    type = EnumField(AnnouncementType, max_length=1, default=AnnouncementType.INFO)

    def __str__(self):
        return self.title
