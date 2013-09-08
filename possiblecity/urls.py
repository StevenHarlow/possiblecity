# urls.py

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, RedirectView

from rest_framework import routers
from apps.lotxlot.views import LotApiViewSet, LotIdeaApiViewSet, PublicLotApiViewSet, PrivateLotApiViewSet
from apps.philadelphia.views import NeighborhoodApiViewSet

router = routers.DefaultRouter()
router.register(r'lots/vacant', LotApiViewSet, base_name='api-lot')
router.register(r'lots/public', PublicLotApiViewSet, base_name='api-public-lot')
router.register(r'lots/private', PrivateLotApiViewSet, base_name='api-private-lot')
router.register(r'lots/ideas', LotIdeaApiViewSet, base_name='api-lot-idea')
router.register(r'philadelphia/neighborhoods', NeighborhoodApiViewSet, base_name='api-neighborhood')


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # admin
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # api
    
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # about
    #url(r'^about/$', RedirectView.as_view(url='/blog/2012/oct/10/introducing-possible-city/'),name='about'),
    
    # blog
    #url(r'^blog/', include('apps.text.urls')),

    # people
    #url(r"^friends/", include("apps.friends.urls")),
    url(
        r"^account/social/connections/$",
        TemplateView.as_view(template_name="account/connections.html"),
        name="account_social_connections"
    ),
    url(r"^account/social/", include("social_auth.urls")),

    url(r"^account/", include("account.urls")),   
    url(r"^people/", include("apps.profiles.urls")),   

    #ideas
    url(r'^ideas/float/', include('apps.ideas.urls.share')),
    url(r'^ideas/explore/', include('apps.ideas.urls.explore')),

    # places
    url(r'^lots/', include('apps.lotxlot.urls')),


    # js urls
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),

    url(r"^likes/", include("phileo.urls")),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

