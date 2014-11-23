from django.conf.urls import patterns, include, url

import ihunt.app.views

urlpatterns = patterns('',
    url(r'^hunt$', ihunt.app.views.hunt, name="hunt"),
    url(r'^help$', ihunt.app.views.help, name="help"),
    url(r'^faq$', ihunt.app.views.faq, name="faq"),
    url(r'^login$', ihunt.app.views.login_view, name="login"),
    url(r'^logout$', ihunt.app.views.logout_view, name="logout"),
    url(r'^$', ihunt.app.views.index, name="index"),
)
