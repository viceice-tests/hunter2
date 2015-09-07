from django.contrib import admin
from ihunt.forms import UserProfileForm
from ihunt.models import Clue, ClueSet, Event, Answer, Guess, Team, UserProfile


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('answer',)


class ClueAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]


class ClueSetAdmin(admin.ModelAdmin):
    pass


class GuessAdmin(admin.ModelAdmin):
    pass


class EventAdmin(admin.ModelAdmin):
    pass


class TeamAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm


admin.site.register(Clue, ClueAdmin)
admin.site.register(ClueSet, ClueSetAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Guess, GuessAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
