from django import forms
from django.contrib import admin
from nested_admin import \
    NestedModelAdmin, \
    NestedStackedInline, \
    NestedTabularInline
from . import models


def make_textinput(field, db_field, kwdict):
    if db_field.attname == field:
        kwdict['widget'] = forms.Textarea(attrs={'rows': 1})


class AnswerInline(NestedTabularInline):
    model = models.Answer
    fields = ('answer', 'runtime')
    extra = 0

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


class GuessAdmin(admin.ModelAdmin):
    pass


class PuzzleAdmin(NestedModelAdmin):
    inlines = [
        FileInline,
        AnswerInline,
        HintInline,
        UnlockInline,
    ]


class EpisodeAdmin(admin.ModelAdmin):
    filter_horizontal = ['puzzles']


class TeamPuzzleDataAdmin(admin.ModelAdmin):
    pass


class UserPuzzleDataAdmin(admin.ModelAdmin):
    readonly_fields = ('token', )


admin.site.register(models.Guess, GuessAdmin)
admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Episode, EpisodeAdmin)
admin.site.register(models.TeamPuzzleData, TeamPuzzleDataAdmin)
admin.site.register(models.UserPuzzleData, UserPuzzleDataAdmin)
admin.site.register(models.Annoucement)
