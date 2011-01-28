from eventmanager.api.handlers import ParticipantHandler, EventHandler, CustomerHandler, FeedbackHandler

from piston.resource import Resource
from django.conf.urls.defaults import *

participant_handler = Resource(ParticipantHandler)
event_handler = Resource(EventHandler)
customer_handler = Resource(CustomerHandler)
feedback_handler = Resource(FeedbackHandler)


urlpatterns = patterns('',
    url(r'^(?P<event_id>\d+)/participant\.(?P<emitter_format>.+)$', participant_handler, name = 'eventmanager_participant_handler'),
    url(r'^(?P<event_id>\d+)/feedback\.(?P<emitter_format>.+)$', feedback_handler, name = 'eventmanager_feedback_handler'),
    url(r'^event\.(?P<emitter_format>.+)$', event_handler, name = 'eventmanager_event_handler'),
    url(r'^customer/(?P<email_hash>\w+)\.(?P<emitter_format>.+)$', customer_handler, name = 'eventmanager_customer_handler'),
)
