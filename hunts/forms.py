from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import Answer, Guess


class AnswerForm(forms.ModelForm):
    # Hidden unless someone tries to add/change an answer that would alter progress due to existing guesses
    alter_progress = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Answer
        fields = ('answer', 'runtime')

    def clean(self, **kwargs):
        cleaned_data = super().clean(**kwargs)

        # We are going to check if changing this answer alters progress. But only if there are no other errors.
        if self.errors:
            return cleaned_data

        # User has ticked the alter progress checkbox
        if cleaned_data.get('alter_progress'):
            return cleaned_data

        try:
            guesses = Guess.objects.filter(for_puzzle=self.instance.for_puzzle)
        except Answer.for_puzzle.RelatedObjectDoesNotExist:
            # We are adding a new puzzle, it won't have any guesses
            return cleaned_data

        old_valid_guesses = [g for g in guesses if self.instance.validate_guess(g)]

        if cleaned_data['DELETE']:
            # If we delete this answer, no guesses will validate against it
            new_valid_guesses = []
        else:
            # Create an answer with the entered data that we can use to validate against
            new_answer = Answer(
                for_puzzle=cleaned_data['for_puzzle'],
                runtime=cleaned_data['runtime'],
                answer=cleaned_data['answer']
            )
            guesses = Guess.objects.filter(for_puzzle=new_answer.for_puzzle)
            new_valid_guesses = [g for g in guesses if new_answer.validate_guess(g)]

        # Has anything actually changed?
        if old_valid_guesses == new_valid_guesses:
            return

        # Sort out who would be affected and how
        new = set(new_valid_guesses) - set(old_valid_guesses)
        removed = set(old_valid_guesses) - set(new_valid_guesses)

        new_teams = self.collect_guesses(new)
        removed_teams = self.collect_guesses(removed)

        # Compose a message and add a checkbox to proceed anyway
        if new_teams or removed_teams:
            msg = "<b>WARNING!</b> You are about to alter this puzzle's answers in a way which will affect teams' progress!\n<br>"
            team_line = '<li>"%s" with guesses: %s</li>'

            # TODO: separate out teams which have another valid answer
            if removed_teams:
                msg += "The following teams will have <b>NO LONGER ANSWERED</b> this puzzle "
                msg += "correctly and will be brought backwards unless they have another valid answer:\n<ul>"
                msg += "\n".join(
                    [team_line % (team.name, ', '.join([g.guess for g in guesses]))
                     for team, guesses in removed_teams.items()]
                )
                msg += "</ul>"
            if new_teams:
                msg += "The following teams will be <b>BROUGHT FORWARD</b> by this change:<br><ul>"
                msg += "\n".join(
                    [team_line % (team.name, ', '.join([g.guess for g in guesses]))
                     for team, guesses in new_teams.items()]
                )
                msg += "</ul>"
            msg += "If you are sure you want to make this change, tick below."

            self.fields['alter_progress'].widget = forms.CheckboxInput()
            if cleaned_data['DELETE']:
                del cleaned_data['DELETE']
            del cleaned_data['alter_progress']
            raise ValidationError(mark_safe(msg))

        return cleaned_data

    def collect_guesses(self, guesses):
        """Collect guesses by team"""

        teams = {}
        for g in guesses:
            t = g.by_team
            if t not in teams:
                teams[t] = []
            teams[t].append(g)

        return teams
