from dal import autocomplete
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory, modelform_factory
from . import models

UserForm = modelform_factory(User, fields=('email', ))

UserProfileFormset = inlineformset_factory(User, models.UserProfile, fields=('seat', ), can_delete=False)


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
        label='Search for a user:',
        queryset=models.UserProfile.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='userprofile_autocomplete',
            attrs={
                'data-minimum-input-length': 1,
            },
        ),
    )


class RequestForm(forms.Form):
    team = forms.ModelChoiceField(
        label='Search for a team:',
        queryset=models.Team.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='team_autocomplete',
            attrs={
                'data-minimum-input-length': 1,
            },
        ),
    )


class CreateTeamForm(forms.ModelForm):
    """Teams are never really created explicitly. Creating a team really means giving a name to your team."""
    class Meta:
        model = models.Team
        fields = ['name']
        labels = {
            'name': 'Choose a name for your team:',
        }


class TeamForm(forms.ModelForm):
    # Hidden unless someone tries to add someone who's already on a team
    move_user = forms.BooleanField(required=False, widget=forms.HiddenInput(), label="Yes, move user")

    class Meta:
        model = models.Team
        fields = ('name', 'at_event', 'members', 'move_user', 'invites', 'requests')
        widgets = {
            'members': autocomplete.ModelSelect2Multiple(
                url='userprofile_autocomplete',
                attrs={'data-minimum-input-length': 1}
            ),
            'invites': autocomplete.ModelSelect2Multiple(
                url='userprofile_autocomplete',
                attrs={'data-minimum-input-length': 1}
            ),
            'requests': autocomplete.ModelSelect2Multiple(
                url='userprofile_autocomplete',
                attrs={'data-minimum-input-length': 1}
            ),
        }

    def clean(self, **kwargs):
        cleaned_data = super().clean(**kwargs)

        # We are going to check if changing this answer alters progress. But only if there are no other errors.
        if self.errors:
            return


        members = cleaned_data.get('members')
        teams = models.Team.objects.filter(at_event=cleaned_data.get('at_event'))
        if self.instance.pk:
            teams = teams.exclude(pk=self.instance.pk)

        moved_members = []
        moved_from = []
        for member in members:
            other_teams = teams.filter(members=member)
            if other_teams.exists():
                moved_members.append(member)
                moved_from.append(other_teams.first())

        if moved_members:
            # User has ticked the alter progress checkbox, move those d00ds
            if cleaned_data.get('move_user'):
                for user, team in zip(moved_members, moved_from):
                    team.members.remove(user)
                    team.save()
                return cleaned_data

            self.fields['move_user'].widget = forms.CheckboxInput()
            member_string = ', '.join(['%s (already on %s)' % (user.user.username, team.name)
                                       for user, team in zip(moved_members, moved_from)])
            self.add_error('move_user', 'You are trying to add %s to this team. Are you sure you want to do this?' % (member_string))
            if len(moved_members) > 1:
                self.fields['move_user'].label = "Yes, move users"

