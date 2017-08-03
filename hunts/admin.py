from django import forms
from django.contrib import admin
from nested_admin import \
    NestedModelAdmin, \
    NestedStackedInline, \
    NestedTabularInline
from . import models
from .forms import AnswerForm


def make_textinput(field, db_field, kwdict):
    if db_field.attname == field:
        kwdict['widget'] = forms.Textarea(attrs={'rows': 1})


class AnswerInline(NestedTabularInline):
    model = models.Answer
    fields = ('answer', 'runtime')
    extra = 0
    form = AnswerForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        make_textinput('answer', db_field, kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)


class FileInline(NestedTabularInline):
    model = models.PuzzleFile
    extra = 0


class HintInline(NestedTabularInline):
    model = models.Hint
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        make_textinput('text', db_field, kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)


class UnlockAnswerInline(NestedStackedInline):
    model = models.UnlockAnswer
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        make_textinput('guess', db_field, kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)


class UnlockInline(NestedStackedInline):
    model = models.Unlock
    inlines = [
        UnlockAnswerInline,
    ]
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        make_textinput('text', db_field, kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(models.Guess)
class GuessAdmin(admin.ModelAdmin):
    read_only_fields = ('correct_current', 'correct_for')


@admin.register(models.Puzzle)
class PuzzleAdmin(NestedModelAdmin):
    inlines = [
        FileInline,
        AnswerInline,
        HintInline,
        UnlockInline,
    ]


@admin.register(models.UserPuzzleData)
class UserPuzzleDataAdmin(admin.ModelAdmin):
    readonly_fields = ('token', )


admin.site.register(models.Annoucement)
admin.site.register(models.Episode)
admin.site.register(models.TeamPuzzleData)
