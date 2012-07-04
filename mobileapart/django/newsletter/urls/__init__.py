from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    url(r'^', include('mobileapart.django.newsletter.urls.newsletter')),
)
