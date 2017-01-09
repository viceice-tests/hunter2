from django.contrib import admin
from . import models
from .forms import UserProfileForm


class TeamAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm

admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
