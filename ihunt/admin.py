from django.contrib import admin
import django.contrib.auth.models as admin_model
from ihunt.models import Clue, ClueSet, Event, Answer, Guess, Team, UserProfile

class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('answer',)

class GuessInline(admin.TabularInline):
    model = Guess
    readonly_fields = ('guess','given')

class EventAdmin(admin.ModelAdmin):
    pass

class ClueSetAdmin(admin.ModelAdmin):
    pass

class ClueAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]

class UserInline(admin.TabularInline):
    model = UserProfile

class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'get_users',
        'current_clue'
    )

    def get_users(self, obj):
        return obj.users.all()
    get_users.short_description = 'Users'


admin.site.register(ClueSet, ClueSetAdmin)
admin.site.register(Clue, ClueAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Event, EventAdmin)
