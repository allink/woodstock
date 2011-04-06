from django.contrib import admin
from django.core import exceptions
from django.db import models
from django.utils.functional import wraps
from django.utils.translation import ugettext_lazy as _

from woodstock import settings
from woodstock.models import Attendance
from woodstock.models import Person

#-----------------------------------------------------------------------------
# Participant
#-----------------------------------------------------------------------------
# callback decorator
def callback(what):
    def actual_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            attendances = function(self, *args, **kwargs)
            if attendances:
                for callback in self.callback_functions:
                    if what in callback['events']:
                        callback['fn'](self,attendances)
            return attendances
        return wrapper
    return actual_decorator


class Participant(Person):
    event_parts = models.ManyToManyField('woodstock.EventPart', related_name="participants",
        blank=True, through="Attendance")
    invitee = models.ForeignKey('woodstock.Invitee', blank=True, null=True,
        default=None, related_name="participants")
        
    class Meta:
        ordering = ('surname',)
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'
        app_label = 'woodstock'
    
    def _attend_events(self, event_parts):
        """
        Attend events without callback and other functianlity.
        """
        attendances = []
        success = True
        for part in event_parts:
            success &= not part.fully_booked()
            attendances.append(Attendance.objects.create(participant=self,
                event_part=part, confirmed=True))
        if success:
            return attendances
        # remove confirmation if something didn't went well
        for attendance in attendances:
            attendance.confirmed = False
            attendance.save()
        return False
        
    @callback('attend_events')
    def attend_events(self, event_parts):
        """
        tries to attend all parts in event_parts
        """
        from woodstock.models import Event        
        if settings.SUBSCRIPTION_CONSUMES_INVITATION and self.attendances.count():
            raise exceptions.PermissionDenied(_("You can only attend one event."))
        if not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS or not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS:
            events = Event.objects.active().filter(
                models.Q(parts__attendances__confirmed=True,parts__attendances__participant=self)
                | models.Q(parts__in=event_parts)
                )
            if not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS and events.distinct().count() > 1:
                raise exceptions.PermissionDenied(_("You can only attend one event."))
            if not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS and events.distinct().count() != events.count():
                raise exceptions.PermissionDenied(_("You can only attend one eventpart per event."))
        attendances = self._attend_events(event_parts)
        if not attendances:
            return False
        # send emails
        for event in Event.objects.for_attendances(attendances):
            event.send_subscribe_mail(self)
        return attendances

    def _cancel_events(self, event_parts, delete=True):
        """
        Cancels event attendances
        """
        if event_parts:
            queryset = self.attendances.filter(event_part__in=event_parts)
        else:
            queryset = self.attendances.all()
        attendances = []
        for attendance in queryset:
            attendances.append(attendance)
            if delete:
                attendance.delete()
        return attendances
    
    @callback('cancel_events')
    def cancel_events(self, event_parts=None):
        """
        Cancels all event attendances to events in event_parts. If event_parts
        is omited all attendances are cancled.
        """
        from woodstock.models import Event
        attendances = self._cancel_events(event_parts)
        # send emails
        for event in Event.objects.filter(parts__in=list(a.event_part for a in attendances)):
            event.send_unsubscribe_mail(self)
        return attendances
        
    @callback('change_events')
    def change_events(self, new_event_parts, old_event_parts=None):
        """
        Changes event attendances. If old_event_parts is omited all current
        attendances are deleted.
        """
        from woodstock.models import Event
        
        old_attendances = self._cancel_events(old_event_parts, delete=False)
        attendances = self._attend_events(new_event_parts)
        if not attendances:
            return False
        for attendance in old_attendances:
            attendance.delete()
        # send emails
        for event in Event.objects.for_attendances(attendances):
            event.send_subscribe_mail(self)
        return attendances
        
    
    def save(self, *args, **kwargs):
        if settings.SUBSCRIPTION_NEEDS_INVITATION and self.invitee is None:
            raise exceptions.PermissionDenied(_("Only invited Persons can register."))
        super(Participant,self).save(*args, **kwargs)
    
    @classmethod
    def register_extension(cls, register_fn):
        register_fn(cls, ParticipantAdmin)
    
    callback_functions = [] # empty array
    
    @classmethod
    def register_callback(cls, callback_fn, events):
        cls.callback_functions.append({'fn':callback_fn, 'events':events})
        
class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('date_registred',)

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'event_parts',)
    readonly_fields = ('invitee',)
    search_fields = ('firstname', 'surname', 'email')
    inlines = (AttendanceInline,)

