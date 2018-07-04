from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('userprofile_autocomplete/', views.UserProfileAutoComplete.as_view(), name='userprofile_autocomplete'),
]
