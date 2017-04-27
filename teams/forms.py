from dal import autocomplete
from django import forms
from . import models

class InviteForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=models.UserProfile.objects.all(),
        widget=autocomplete.ModelSelect2(url='userprofile_autocomplete'),
    )
