from allauth.account.forms import ChangePasswordForm, SetPasswordForm
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View

from . import forms, models


class UserProfileAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = models.UserProfile.objects.exclude(pk=self.request.user.profile.pk).order_by('user__username')

        if self.q:
            qs = qs.filter(
                Q(user__username__istartswith=self.q) |
                Q(user__email__istartswith=self.q)
            )

        return qs


class EditProfileView(LoginRequiredMixin, View):

    def get(self, request):
        user_form = forms.UserForm(instance=request.user)
        password_form = ChangePasswordForm(user=request.user) if request.user.has_usable_password() else SetPasswordForm(user=request.user)
        profile_formset = forms.UserProfileFormset(instance=request.user)
        steam_linked = request.user.socialaccount_set.exists()  # This condition breaks down if we support multiple social accounts.
        context = {
            'user_form': user_form,
            'password_form': password_form,
            'profile_formset': profile_formset,
            'steam_linked': steam_linked,
        }
        return TemplateResponse(
            request,
            'teams/profile.html',
            context=context,
        )

    def post(self, request):
        user_form = forms.UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            created_user = user_form.save(commit=False)
            profile_formset = forms.UserProfileFormset(request.POST, instance=created_user)
            if profile_formset.is_valid():
                created_user.save()
                profile_formset.save()
                return HttpResponseRedirect(reverse('edit_profile', subdomain='www'))
