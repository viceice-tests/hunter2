from dal import autocomplete
from django import forms
from . import models


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ['seat']

    field_order = ['username', 'email', 'password1', 'password2', 'seat']

    def signup(self, request, user):
        user.profile = models.UserProfile(user=user)
        user.profile.seat = self.cleaned_data['seat']
        user.profile.save()
        user.save()


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
            instance.invites.add(*models.UserProfile.objects.filter(pk__in=self.cleaned_data['invites']))

        return instance
