from django.contrib import admin
from . import models


class FileInline(admin.TabularInline):
    model = models.EventFile
    extra = 0


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [
        FileInline,
    ]


admin.site.register(models.Domain)
admin.site.register(models.Theme)
