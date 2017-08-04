from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import Puzzle, Answer, Guess


class AnswerForm(forms.ModelForm):
    alter_progress = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Answer
        fields = ('answer', 'runtime')

    def clean(self, **kwargs):
        cleaned_data = super().clean(**kwargs)

        # We are going to check if changing this answer alters progress. But only if there are no other errors.
        if self.errors:
            return

        # User as ticked the alter progress checkbox
        if cleaned_data.get('alter_progress'):
            return cleaned_data

        guesses = Guess.objects.filter(for_puzzle=self.instance.for_puzzle)
        old_valid_guesses = [g for g in guesses if self.instance.validate_guess(g)]

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

        new = set(new_valid_guesses) - set(old_valid_guesses)
        removed = set(old_valid_guesses) - set(new_valid_guesses)

        new_teams = {}
        for g in new:
            t = g.by_team
            if t not in new_teams:
                new_teams[t] = []
            new_teams[t].append(g)

        removed_teams = {}
        for g in removed:
            t = g.by_team
            if t not in removed_teams:
                removed_teams[t] = []
            removed_teams[t].append(g)

        if new_teams or removed_teams:
            msg = "<b>WARNING!</b> You are about to alter this puzzle's answers in a way which will affect teams' progress!<br>"
            if removed_teams:
                msg += "The following teams will have NO LONGER ANSWERED this puzzle correctly and will be brought backwards:<br><ul>"
                msg += "\n".join(["<li>%s with guesses %s</li>" % (team.name, ', '.join([g.guess for g in guesses])) for team, guesses in removed_teams.items()])
                msg += "</ul>"
            if new_teams:
                msg += "The following teams will be BROUGHT FORWARD by this change:<br><ul>"
                msg += "\n".join(['<li>"%s" with guesses: %s</li>' % (team.name, ', '.join([g.guess for g in guesses])) for team, guesses in new_teams.items()])
                msg += "</ul>"
            msg += "If you are sure you want to make this change, tick below."

            self.fields['alter_progress'].widget = forms.CheckboxInput()
            del cleaned_data['alter_progress']
            raise ValidationError(mark_safe(msg))

        return cleaned_data
