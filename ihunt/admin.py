from django.contrib import admin
from ihunt.forms import UserProfileForm
from ihunt.models import Puzzle, PuzzleSet, Hint, Unlock, UnlockGuess, Event, Answer, Guess, Team, UserProfile
from nested_admin import NestedAdmin, NestedStackedInline


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('answer',)
    extra = 0


class HintInline(admin.TabularInline):
    model = Hint
    extra = 0


class UnlockGuessInline(NestedStackedInline):
    model = UnlockGuess
    extra = 0


class UnlockInline(NestedStackedInline):
    model = Unlock
    inlines = [
        UnlockGuessInline,
    ]
    extra = 0


class PuzzleAdmin(NestedAdmin):
    inlines = [
        AnswerInline,
        HintInline,
        UnlockInline,
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
