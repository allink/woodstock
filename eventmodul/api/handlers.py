from eventmanager.models import Participant, Event, Customer, Feedback
from eventmanager.forms import ParticipantForm, FeedbackForm

from piston.utils import validate
from piston.handler import BaseHandler
from piston.utils import rc

from django.utils import translation
from django.http import HttpResponse
from django.utils.translation import ugettext as _

import simplejson

class ParticipantHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = Participant
    
    def create(self, request, event_id):
        event = Event.objects.filter(id=event_id).all()[0]
        participant = Participant(language=translation.get_language())
        form = ParticipantForm(request.POST, instance=participant)
        if not form.is_valid():
            resp = HttpResponse(
                simplejson.dumps(
                    dict(
                        (k, map(unicode, v))
                        for (k,v) in form.errors.iteritems()
                    )
                )
            )
            resp.status_code = 400
            return resp
        # check if email already registred to this event
        p = Participant.objects.filter(email=form.cleaned_data['email']).filter(events__id=event.id)
        if p.count() > 0:
            resp = HttpResponse(
                simplejson.dumps({
                    'email' : _("Address already used.")
                })
            )
            resp.status_code = 400
            return resp
        form.save()
        if request.session.get('customer_id', False):
            customer=Customer.objects.filter(id=request.session.get('customer_id'))[0]
            form.instance.customer = customer
            form.instance.save()
        if form.instance.attend_event(event):
            return rc.CREATED
        else:
            return HttpResponse(status=202)
        

class FeedbackHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = Feedback
    
    def create(self, request, event_id):
        event = Event.objects.filter(id=event_id).all()[0]
        feedback = Feedback(event=event)
        form = FeedbackForm(request.POST, instance=feedback)
        if not form.is_valid():
            resp = HttpResponse(
                simplejson.dumps(
                    dict(
                        (k, map(unicode, v))
                        for (k,v) in form.errors.iteritems()
                    )
                )
            )
            resp.status_code = 400
            return resp
        form.save()
        return rc.CREATED


class EventHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Event
    
class CustomerHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Customer
    exclude = ('email_hash', 'done')