from woodstock.models.extendable import ExtendableMixin
from woodstock.models.attendance import Attendance    
from woodstock.models.event_part import EventPart
from woodstock.models.person import Person
from woodstock.models.participant import Participant
from woodstock.models.event import Event
from woodstock.models.group import Group
from woodstock.models.invitee import Invitee
from woodstock.models.salutation import Salutation

__all__ = ('Attendance', 'Event', 'EventPart', 'Group', 'Invitee', 'Participant', 'Salutation')

# register view links
from pennyblack.models import Newsletter
from woodstock.views.ics import event_parts_email_view
Newsletter.register_view_link('woodstock.event_parts_ics', event_parts_email_view)
