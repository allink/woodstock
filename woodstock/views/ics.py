from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from woodstock.models import EventPart
from woodstock.views.decorators import registration_required
from woodstock import settings

import icalendar
import datetime
import random
import hashlib

def _event_part_ics(event_parts):
    cal = icalendar.Calendar()
    cal.add('prodid', '-//Woodstock//')
    cal.add('version', '2.0')
    for event_part in event_parts:
        event = icalendar.Event()
        event.add('summary', settings.ICS_EVENT_PART_NAME % {'event_name':event_part.event.translation.name, 'part_name':event_part.name})
        event.add('dtstart', event_part.date_start)
        event.add('dtend', event_part.date_end)
        event.add('dtstamp', datetime.datetime.now())
        event['uid'] = '%s/%s/woodstock' % (event_part.id, hashlib.md5(str(random.random())).hexdigest()[:10])
        event.add('priority', 5)
        cal.add_component(event)
    response = HttpResponse(cal.as_string(),mimetype="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=event.ics'
    return response

def event_part_view(request, event_part_id):
    event_part = get_object_or_404(EventPart, pk=event_part_id)
    ics = _event_part_ics([event_part])
    response = HttpResponse(ics,mimetype="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=event.ics'
    return response


def event_parts_email_view(request, participant, event):
    """
    This view is showed using the pennyblack proxy view.
    """
    event_parts = EventPart.objects.filter(event=event, attendances__participant=participant)
    ics = _event_part_ics(event_parts)
    response = HttpResponse(ics,mimetype="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=event.ics'
    return response
