from eventmodul.models import Event, Customer, Participant, NewsletterMail, Group, Feedback
from eventmodul.forms import ParticipantForm, FeedbackForm

from feincms.content.application.models import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import translation
from django.conf import settings

import os

def index(request):
    return render_to_response(
        'index.html',
        {
            'events': Event.objects.order_by('date'),
        },
        context_instance = RequestContext(request),
    )
    

def detail(request, object_id):
    return render_to_response(
        'detail.html',
        {
            'event': Event.objects.filter(id=object_id).all()[0]
        },
        context_instance = RequestContext(request),
    )

def signup(request, object_id):
    event = Event.objects.filter(id=object_id).all()[0]
    success = False
    fully_booked = False
    if request.method == 'POST':
        p = Participant(language=translation.get_language())
        form = ParticipantForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            success = form.instance.attend_event(event)
            fully_booked = not success
    else:
        if request.session.get('customer_id', False):
            customer=Customer.objects.filter(id=request.session.get('customer_id'))[0]
            form = ParticipantForm(instance=customer)
        else:
            form = ParticipantForm()
    return render_to_response(
        'signup.html',
        {
            'form': form,
            'event': event,
            'success': success,
            'fully_booked': fully_booked
        },
        context_instance = RequestContext(request),
    )
