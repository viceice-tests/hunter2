from django.db import models
from django.contrib.auth.models import User


class Clue(models.Model):
    title = models.TextField(unique=True)
    content = models.TextField()

    def __unicode__(self):
        return "<Clue: {}>".format(self.title)


class ClueSet(models.Model):
    clues = models.ManyToManyField(Clue)
    start_date = models.DateTimeField()


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


