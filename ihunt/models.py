from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

class Event(models.Model):
    name = models.TextField(unique=True)
    theme = models.TextField()
    current = models.BooleanField(default=False)

    def __unicode__(self):
        return "<Event: {}>".format(self.name)

    def clean(self):
        if self.current:
            if Event.objects.filter(current=True).count() > 0:
                raise ValidationError("There can only be one current event")

class Clue(models.Model):
    title = models.TextField(unique=True)
    content = models.TextField()

    def __unicode__(self):
        return "<Clue: {}>".format(self.title)


class ClueSet(models.Model):
    clues = models.ManyToManyField(Clue)
    start_date = models.DateTimeField()
    event = models.ForeignKey(Event, related_name="cluesets")


class Answer(models.Model):
    for_clue = models.ForeignKey(Clue)
    answer = models.TextField()

    def __unicode__(self):
        return "<Answer: {}>".format(self.answer)


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    current_clue = models.ForeignKey(Clue)
    current_clueset = models.ForeignKey(ClueSet)

    def __unicode__(self):
        return "<Team: {}>".format(self.name)

    def add_user(self, user):
        user.team = self
        user.save()


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    team = models.ForeignKey(Team, related_name="users")

    def __unicode__(self):
        return "<UserProfile: {}>".format(self.user.username)

class Guess(models.Model):
    for_clue = models.ForeignKey(Clue)
    by = models.ForeignKey(UserProfile)
    guess = models.TextField()
    given = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "<Guess: {} by {} ({})>".format(
            self.guess, self.by.user.username, self.by.team.name)


