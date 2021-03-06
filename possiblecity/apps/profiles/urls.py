# profiles/urls.py

from django.conf.urls.defaults import patterns, url

from .views import ProfileDetailView, ProfileListView, ProfileUpdateView, ProfileLoginView

urlpatterns = patterns('',
    url(r'^$', ProfileListView.as_view(), name='profiles_profile_list'),
    url(r'^update/$', ProfileUpdateView.as_view(), 
        name='profiles_profile_update'),
    url(r'^profile/(?P<username>[\w\.\@\+\-]+)/$', ProfileDetailView.as_view(), name='profiles_profile_detail'),
    url(r'^profile/$', ProfileLoginView.as_view(), 
        name='profiles_profile_login'),
)
