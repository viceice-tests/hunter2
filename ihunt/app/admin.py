from django.contrib import admin
import django.contrib.auth.models as admin_model
from ihunt.app.models import Clue, ClueSet, Answer, Guess, Team, UserProfile

class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('answer',)

class GuessInline(admin.TabularInline):
    model = Guess
    readonly_fields = ('guess','given')

class ClueSetAdmin(admin.ModelAdmin):
    pass

class ClueAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
        GuessInline
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
