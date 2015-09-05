from django.contrib import admin
from ihunt.forms import UserProfileForm
from ihunt.models import Clue, ClueSet, Event, Answer, Guess, Team, UserProfile


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('answer',)


class GuessInline(admin.TabularInline):
    model = Guess
    readonly_fields = ('guess', 'given')


class EventAdmin(admin.ModelAdmin):
    pass


class ClueSetAdmin(admin.ModelAdmin):
    pass


class ClueAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm


class TeamAdmin(admin.ModelAdmin):
    pass


admin.site.register(Clue, ClueAdmin)
admin.site.register(ClueSet, ClueSetAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
