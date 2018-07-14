from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory, modelform_factory

from events.models import Attendance
from . import models

UserForm = modelform_factory(User, fields=('email', ))

UserProfileFormset = inlineformset_factory(User, models.UserProfile, fields=[], can_delete=False)

AttendanceFormset = inlineformset_factory(models.UserProfile, Attendance, fields=('seat', ), extra=0, can_delete=False)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = []

    field_order = ['username', 'email', 'password1', 'password2']

    def signup(self, request, user):
        user.profile = models.UserProfile(user=user)
        user.profile.save()
        user.save()
