from django import forms
from django.contrib.auth.models import User
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
