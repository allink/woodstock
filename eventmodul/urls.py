from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'eventmodul.views.index', name='event_index'),
    url(r'^(?P<object_id>\d+)/$', 'eventmodul.views.detail', name='event_detail'),
    url(r'^(?P<object_id>\d+)/signup/$', 'eventmodul.views.signup', name='event_signup'),
)
