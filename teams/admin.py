from django.contrib import admin
from django.db.models import Count

from .forms import TeamForm
from . import models


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamForm
    ordering = ['at_event', 'name']
    list_display = ('name', 'at_event', 'is_admin', 'member_count')
    list_display_links = ('name', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            member_count=Count('members', distinct=True)
        )

    def member_count(self, team):
        return team.member_count

    member_count.short_description = "Members"


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ordering = ['pk']
    list_display = ('username', 'seat', 'email')
    list_display_links = ('username', )
    list_select_related = ('user', )

    def username(self, profile):
        return profile.user.username

    def email(self, profile):
        return profile.user.email
