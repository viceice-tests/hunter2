from django.contrib import admin

from .forms import TeamForm
from . import models


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamForm
    ordering = ['at_event', 'name']
    list_display = ('the_name', 'at_event', 'is_admin', 'member_count')
    list_display_links = ('the_name', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('members', 'members__user')

    def member_count(self, team):
        return team.members.all().count()

    member_count.short_description = "Members"

    def the_name(self, team):
        return team.get_verbose_name()

    the_name.short_description = "Name"
    the_name.admin_order_field = "name"
