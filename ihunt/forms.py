from django import forms
from django.core.exceptions import ValidationError
from ihunt.models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = []

    def clean(self):
        events = set()
        print(self.cleaned_data['teams'])
        for team in self.cleaned_data['teams']:
            if team.at_event in events:
                raise ValidationError(
                    "Cannot join multiple teams at the same event"
                )
            events.add(team.at_event)
