from django.http import HttpResponseRedirect

from woodstock import settings
from woodstock.models import Event

try:
    from feincms.content.application.models import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def next_active_event(request):
    try:
        event = Event.objects.pending()[0]
    except IndexError:
        try:
            event = Event.objects.active()[0]
        except IndexError:
            return HttpResponseRedirect('/')
    return HttpResponseRedirect(reverse(settings.EVENT_DETAIL_URL_NAME, args=(event.slug,)))
