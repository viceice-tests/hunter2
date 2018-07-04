from django.urls import include, path
from . import views

teampatterns = [
    path('', views.TeamView.as_view(), name='team'),
    path('invite', views.Invite.as_view(), name='invite'),
    path('cancelinvite', views.CancelInvite.as_view(), name='cancelinvite'),
    path('acceptinvite', views.AcceptInvite.as_view(), name='acceptinvite'),
    path('denyinvite', views.DenyInvite.as_view(), name='denyinvite'),
    path('request', views.Request.as_view(), name='request'),
    path('cancelrequest', views.CancelRequest.as_view(), name='cancelrequest'),
    path('acceptrequest', views.AcceptRequest.as_view(), name='acceptrequest'),
    path('denyrequest', views.DenyRequest.as_view(), name='denyrequest'),
]

eventpatterns = [
    path('team/', views.ManageTeamView.as_view(), name='manage_team'),
    path('team/create', views.CreateTeamView.as_view(), name='create_team'),
    path('team/<int:team_id>/', include(teampatterns), name='team'),
]

urlpatterns = [
    path('hunt/', include(eventpatterns)),
    path('team_autocomplete', views.TeamAutoComplete.as_view(), name='team_autocomplete'),
]
