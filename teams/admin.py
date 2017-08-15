from django.contrib import admin

from . import models


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    ordering = ['at_event', 'name']
    list_display = ('name', 'at_event', 'is_admin', 'member_count')
    list_display_links = ('name', )

    def member_count(self, obj: models.Team):
        return obj.members.count()

    member_count.short_description = "Members"


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ordering = ['pk']
    list_display = ('username', 'seat', 'email')
    list_display_links = ('username', )

    def username(self, obj: models.UserProfile):
        return obj.user.username

    def email(self, obj: models.UserProfile):
        return obj.user.email
