from django.contrib import admin

from . import models


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
