from eventmodul.models import Event, EventPart, Participant
from eventmodul.forms import ParticipantForm

from feincms.content.application.models import reverse

from django.conf import settings
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation

def index(request):
    return render_to_response(
        'index.html',
        {
            'events': Event.objects.active(),
        },
        context_instance = RequestContext(request),
    )
    

def detail(request, object_id):
    return render_to_response(
        'detail.html',
        {
            'event': Event.objects.active().get(id=object_id)
        },
        context_instance = RequestContext(request),
    )

def signup(request, object_id):
    """
    Signup view with all possible parts of an event listed and selectable
    """
    event = Event.objects.active().get(id=object_id)
    if request.method == 'POST':
        p = Participant(language=translation.get_language())
        form = ParticipantForm(request.POST, instance=p, event_parts_queryset=event.parts.active())
        if form.is_valid():
            form.save()
            success = form.instance.attend_events(form.cleaned_data['event_parts'])
    else:
        if request.session.get('customer_id', False):
            customer=Customer.objects.filter(id=request.session.get('customer_id'))[0]
            form = ParticipantForm(instance=customer, event_parts_queryset=event.parts.active())
        else:
            form = ParticipantForm(event_parts_queryset=event.parts.active())
    context = {'form': form, 'event': event}
    context.update(csrf(request))
    return render_to_response(
        'signup.html',
        context,
        context_instance = RequestContext(request),
    )
