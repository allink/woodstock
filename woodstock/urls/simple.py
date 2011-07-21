"""
Simple url pattern with index page, detail pate and signup page
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'woodstock.views.simple.index', name='event_index'),
    url(r'^(?P<object_id>\d+)/$', 'woodstock.views.simple.detail', name='event_detail'),
    url(r'^(?P<object_id>\d+)/signup/$', 'woodstock.views.simple.signup', name='event_signup'),
)
