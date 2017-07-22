from django.contrib import admin
from nested_admin import \
    NestedModelAdmin, \
    NestedStackedInline, \
    NestedTabularInline
from . import models


class AnswerInline(NestedTabularInline):
    model = models.Answer
    fields = ('answer', 'runtime')
    extra = 0


class FileInline(NestedTabularInline):
    model = models.PuzzleFile
    extra = 0


class HintInline(NestedTabularInline):
    model = models.Hint
    extra = 0


class UnlockAnswerInline(NestedStackedInline):
    model = models.UnlockAnswer
    extra = 0


class UnlockInline(NestedStackedInline):
    model = models.Unlock
    inlines = [
        UnlockAnswerInline,
    ]
    extra = 0


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
    pass


class TeamPuzzleDataAdmin(admin.ModelAdmin):
    pass


class UserPuzzleDataAdmin(admin.ModelAdmin):
    readonly_fields = ('token', )


admin.site.register(models.Guess, GuessAdmin)
admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Episode, EpisodeAdmin)
admin.site.register(models.TeamPuzzleData, TeamPuzzleDataAdmin)
admin.site.register(models.UserPuzzleData, UserPuzzleDataAdmin)
