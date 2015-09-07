from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField
from time import strftime


@python_2_unicode_compatible
class Event(models.Model):
    name = models.TextField(unique=True)
    theme = models.TextField()
    current = models.BooleanField(default=False)

    def __str__(self):
        return '<Event: {}>'.format(self.name)

    def clean(self):
        if self.current and Event.objects.filter(current=True).count() > 0:
            raise ValidationError('There can only be one current event')


@python_2_unicode_compatible
class Clue(models.Model):
    title = models.TextField(unique=True)
    content = models.TextField()

    def __str__(self):
        return '<Clue: {}>'.format(self.title)


@python_2_unicode_compatible
class ClueSet(models.Model):
    clues = SortedManyToManyField(Clue)
    start_date = models.DateTimeField()
    event = models.ForeignKey(Event, related_name='cluesets')

    def __str__(self):
        return '<ClueSet: {} - {}>'.format(
            self.event.name, strftime('%A %H:%M', self.start_date.timetuple())
        )


@python_2_unicode_compatible
class Answer(models.Model):
    for_clue = models.ForeignKey(Clue, related_name='answers')
    answer = models.TextField()

    def __str__(self):
        return '<Answer: {}>'.format(self.answer)


@python_2_unicode_compatible
class Team(models.Model):
    class Meta:
        unique_together = (('name', 'at_event'), )

    name = models.CharField(max_length=100)
    at_event = models.ForeignKey(Event, related_name='event')

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
    for_clue = models.ForeignKey(Clue)
    by = models.ForeignKey(UserProfile)
    guess = models.TextField()
    given = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Guesses'

    def __str__(self):
        return '<Guess: {} by {}>'.format(
            self.guess, self.by.user.username
        )

    def is_right():
        for answer in for_clue.Answer_set:
            if answer == guess:
                return True
        return False
