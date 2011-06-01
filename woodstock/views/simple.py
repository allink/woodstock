from woodstock import settings
from woodstock.models import Event, EventPart
from woodstock.forms import ParticipantForm
from woodstock.views import get_redirect_url
from woodstock.views.decorators import registration_required, \
    invitation_required

from feincms.content.application.models import reverse

from django.contrib import messages
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

def index(request):
    return render_to_response(
        'woodstock/simple/index.html',
        {
            'events': Event.objects.active(),
        },
        context_instance = RequestContext(request),
    )

index_invitation_required = invitation_required(index)
index_registration_required = registration_required(index)


def detail(request, slug):
    event = Event.objects.get_by_slug(slug)
    return render_to_response(
        'woodstock/simple/detail.html',
        {
            'event': event,
        },
        context_instance = RequestContext(request),
    )

detail_invitation_required = invitation_required(detail)
detail_registration_required = registration_required(detail)

@csrf_protect
def signup(request, slug, participant_form=ParticipantForm):
    """
    Signup view with all possible parts of an event listed and selectable
    """
    event = Event.objects.get_by_slug(slug)
    if request.method == 'POST':
        form = ParticipantForm(request.POST, request=request, event_parts_queryset=event.parts.active())
        if form.is_valid():
            if form.save():
                messages.success(request, settings.MESSAGES_SIMPLE_SIGNUP_SUCCESS)
                return HttpResponseRedirect(get_redirect_url(settings.POST_ACTION_REDIRECT_URL))
            else:
                messages.error(request, settings.MESSAGES_SIMPLE_SIGNUP_FAILED)
                return HttpResponseRedirect(get_redirect_url(settings.POST_ACTION_REDIRECT_URL))
    else:
        form = ParticipantForm(request=request , event_parts_queryset=event.parts.active())
    context = {'form': form, 'event': event}
    context.update(csrf(request))
    return render_to_response(
        'woodstock/simple/signup.html',
        context,
        context_instance = RequestContext(request),
    )

signup_invitation_required = invitation_required(signup)
signup_registration_required = registration_required(signup)
