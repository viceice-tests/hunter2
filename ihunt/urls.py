from django.conf.urls import patterns, include, url

import ihunt.views

eventpatterns = patterns(
    '',
    url(r'hunt$', ihunt.views.hunt, name='hunt'),
    url(r'puzzle/(?P<puzzle_id>[0-9]+)$', ihunt.views.puzzle, name='puzzle'),
)

urlpatterns = patterns(
    '',
    url(r'^event/(?P<event_id>[0-9]+)/', include(eventpatterns)),
    url(r'^faq$', ihunt.views.faq, name='faq'),
    url(r'^help$', ihunt.views.help, name='help'),
    url(r'^login$', ihunt.views.login_view, name='login'),
    url(r'^logout$', ihunt.views.logout_view, name='logout'),
    url(r'', include(eventpatterns)),
    url(r'^$', ihunt.views.index, name='index'),
)
