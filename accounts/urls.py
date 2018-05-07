from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^profile/$', views.EditProfileView.as_view(), name='edit_profile'),
    url(r'^userprofile_autocomplete/$', views.UserProfileAutoComplete.as_view(), name='userprofile_autocomplete'),
]
