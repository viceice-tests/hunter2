from django.contrib import admin
from . import models


class EventAdmin(admin.ModelAdmin):
    pass


class ThemeAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Theme, ThemeAdmin)
