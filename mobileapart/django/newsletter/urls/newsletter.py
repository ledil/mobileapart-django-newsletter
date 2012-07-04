from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('mobileapart.django.newsletter.views',
    url(r'^preview/(?P<nid>[-\w]+)/(?P<cid>[-\w]+)$', 'view_newsletter_preview', name='newsletter_newsletter_preview'),
    url(r'^unsubscribe/(?P<nid>[-\w]+)/(?P<cid>[-\w]+)$', 'view_newsletter_unsubscribe', name='newsletter_newsletter_unsubscribe'),
    url(r'^tracking/(?P<nid>[-\w]+)/(?P<cid>[-\w]+)$', 'view_newsletter_tracking', name='newsletter_newsletter_tracking'),
    url(r'^subscribe/(?P<nid>[-\w]+)/(?P<cid>[-\w]+)$', 'view_newsletter_subscribe', name='newsletter_newsletter_subscribe'),
)    
