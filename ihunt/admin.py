from django.contrib import admin
from ihunt.forms import UserProfileForm
from ihunt.models import Puzzle, PuzzleSet, Event, Answer, Guess, Team, UserProfile


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('answer',)


class PuzzleAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]


class PuzzleSetAdmin(admin.ModelAdmin):
    pass


class GuessAdmin(admin.ModelAdmin):
    pass


class EventAdmin(admin.ModelAdmin):
    pass


class TeamAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm


admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(PuzzleSet, PuzzleSetAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Guess, GuessAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
