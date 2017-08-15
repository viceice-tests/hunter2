from django.contrib import admin
from .forms import TeamForm
from . import models


class TeamAdmin(admin.ModelAdmin):
    form = TeamForm


class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
