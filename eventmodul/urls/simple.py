"""
Simple url pattern with index page, detail pate and signup page
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'eventmodul.views.simple.index', name='event_index'),
    url(r'^(?P<object_id>\d+)/$', 'eventmodul.views.simple.detail', name='event_detail'),
    url(r'^(?P<object_id>\d+)/signup/$', 'eventmodul.views.simple.signup', name='event_signup'),
)
