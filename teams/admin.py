from django.contrib import admin
from . import models


class TeamAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
