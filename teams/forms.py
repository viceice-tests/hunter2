from dal import autocomplete
from django import forms
from . import models

class InviteForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=models.UserProfile.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='userprofile_autocomplete',
            attrs={
                'data-minimum-input-length': 1,
            },
        ),
    )

class TeamForm(forms.ModelForm):
    def __init__(self, *args, event, user, **kwargs):
        self.event = event
        self.user = user
        super(TeamForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Team
        fields = ['name', 'invites']
        widgets = {
            'invites': autocomplete.ModelSelect2Multiple(
                url='userprofile_autocomplete',
                attrs={
                    'data-minimum-input-length': 1,
                },
            ),
        }

    def save(self, commit=True):
        instance = super(TeamForm, self).save(commit=False)
        instance.at_event = self.event

        if commit:
            instance.save()
            instance.members.add(self.user)

        return instance
