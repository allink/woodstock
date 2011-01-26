from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, Template
from django.template.defaultfilters import slugify

from pennyblack.options import NewsletterReceiverMixin, JobUnitMixin, \
    JobUnitAdmin

from eventmodul import settings

from feincms.module.medialibrary.models import MediaFile
from feincms.translations import TranslatedObjectMixin, Translation, \
    TranslatedObjectManager

import random
import sys
import csv
from datetime import datetime

try:
    import xlwt
except ImportError:
    EXCEL_EXPORT_ACTIVE = False
else:
    EXCEL_EXPORT_ACTIVE = True


class ExtendableMixin(object):
    @classmethod
    def register_extension(cls, register_fn):
        """
        Call the register function of an extension. You must override this
        if you provide a custom ModelAdmin class and want your extensions to
        be able to patch stuff in.
        """
        register_fn(cls, None)

#-----------------------------------------------------------------------------
# EventPart
#-----------------------------------------------------------------------------
class EventPartManager(models.Manager):
    use_for_related_fields = True
    def active(self):
        """
        Filters all active Eventparts
        """
        return self.filter(active=True)

class EventPart(models.Model):
    event = models.ForeignKey('Event', related_name="parts")
    name = models.CharField(max_length=100)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    signable = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    maximum_participants = models.IntegerField(default=0,
        verbose_name="Maximum Participants",
        help_text="Number of maximum participants or 0 for no limit.")
    
    objects = EventPartManager()
    
    class Meta:
        ordering = ('date_start',)
        verbose_name = "Event Part"
        verbose_name_plural = "Event Parts"
    
    def __unicode__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        super(EventPart,self).save(*args,**kwargs)
        self.event.update_dates()
    
    def fully_booked(self):
        """Returns true if event is already fully booked"""
        return self.maximum_participants and self.get_participant_count() >= self.maximum_participants
    
    def get_participant_count(self):
        return self.participants.count()
    get_participant_count.short_description = "Participants"

class EventPartInline(admin.TabularInline):
    model = EventPart
    readonly_fields = ('get_participant_count',)
    extra = 0

#-----------------------------------------------------------------------------
# Event
#-----------------------------------------------------------------------------
class EventManager(models.Manager, ExtendableMixin):
    def active(self):
        """
        Filters all active Events
        """
        return self.filter(active=True)
    
    def get_by_slug(self, slug, active=True):
        """
        Gets the event corresponding to slug
        """
        if not active:
            return self.get(slug=slug)
        return self.active().get(slug=slug)
    
    def pending(self):
        """
        Gives all events which ar not already passed.
        """
        return self.active().filter(date_end__lt=datetime.now())

class Event(models.Model, TranslatedObjectMixin, JobUnitMixin, ExtendableMixin):
    active = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    date_start = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    
    objects = EventManager()
    class Meta:
        ordering = ('date_start',)
        verbose_name = "Event"
        verbose_name_plural = "Events"
    
    def __unicode__(self):
        try:
            return self.translation.name
        except exceptions.ObjectDoesNotExist:
            return 'no name'
    
    def update_dates(self):
        first_part = self.parts.active().order_by('date_start')[0]
        self.date_start = first_part.date_start
        last_part = self.parts.active().order_by('-date_start')[0]
        self.date_end = last_part.date_end
        self.save()
    
    @property
    def participant_count(self):
        return self.parts.active().aggregate(models.Count('participants__id'))['participants__id__count']
    
    def get_participant_count(self):
        count = 0
        for event_part in self.parts.all():
            count += event_part.get_participant_count()
        return count
    get_participant_count.short_description = "Participants"
    
    @property
    def available_places(self):
        return self. max_participants - self.participant_count
    
    @property
    def max_participants(self):
        if self.parts.active().filter(maximum_participants=0).count():
            return 0
        else:
            return self.parts.active().aggregate(models.Sum('maximum_participants'))['maximum_participants__sum']
    
    def get_max_participants(self):
        return self.max_participants or 'Unlimitiert'
    get_max_participants.short_description = "Maximum Participants"
    
    # newsletter functions
    def get_newsletter_receiver_collections(self):
        collections = tuple()
        for part in self.parts.all():
            collections += ((part.name,'get_newsletter_receivers',
                {'event_part':part.id}),)
        return collections
    
    def get_newsletter_receivers(self, event_part_id=None):
        if event_part_id:
            return self.parts.get(id=event_part_id).participants.all()
    
    def get_receiver_filtered_queryset(self, collections=None, **kwargs):
        q = Q()
        for collection in collections:
            q |= Q(events__pk=int(collection))
            print Participant.objects.filter(events__pk=int(collection))
        print Participant.objects.filter(q)
        return Participant.objects.filter(q)
    
    def send_subscribe_mail(self, participant):
        if self.translation.subscribe_mail is None:
            return
        self.translation.subscribe_mail.send(participant, group=self)
    
    def send_unsubscribe_mail(self, participant):
        if self.translation.unsubscribe_mail is None:
            return
        self.translation.unsubscribe_mail.send(participant, group=self)
    
    @classmethod
    def register_extension(cls, register_fn):
        register_fn(cls, EventAdmin, EventTranslation, EventTranslationInline, EventPart, EventPartInline)


class EventTranslation(Translation(Event)):
    name = models.CharField(max_length=100)
    subscribe_mail = models.ForeignKey('pennyblack.Newsletter', blank=True,
        null=True, related_name="signup_events")
    unsubscribe_mail = models.ForeignKey('pennyblack.Newsletter', blank=True,
        null=True, related_name="signoff_events")

class EventTranslationInline(admin.StackedInline):
    model = EventTranslation
    max_num = len(settings.LANGUAGES)

class EventAdmin(JobUnitAdmin):
    inlines = (EventTranslationInline, EventPartInline,)
    list_display = ('__unicode__', 'active', 'get_participant_count', 'get_max_participants')
    readonly_fields = ('date_start', 'date_end')
    collection_selection_form_extra_fields = {
        'attended': forms.BooleanField(required=False),
        'confirmed': forms.BooleanField(required=False),
    }
    
    def tool_excel_export(self, request, obj, button):
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % (slugify(obj.name),)
        
        wb = xlwt.Workbook()
        ws = wb.add_sheet(slugify(obj.name))
        row = 0
        
        ws.write(row, 0, 'Firstname')
        ws.write(row, 1, 'Surname')
        ws.write(row, 2, 'Company')
        ws.write(row, 3, 'Location')
        ws.write(row, 4, 'Email')
        ws.write(row, 5, 'Language')
        ws.write(row, 6, 'Registred')
        row += 1
        
        for participant in obj.participants.all():
            ws.write(row, 0, participant.firstname)
            ws.write(row, 1, participant.surname)
            ws.write(row, 2, participant.company)
            ws.write(row, 3, participant.location)
            ws.write(row, 4, participant.email)
            ws.write(row, 5, participant.language)
            ws.write(row, 6, participant.date_registred.strftime('%d.%m.%Y %H:%M'))
            row += 1
        
        wb.save(response)
        return response

#-----------------------------------------------------------------------------
# Group
#-----------------------------------------------------------------------------
class Group(models.Model, JobUnitMixin):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, null=True, blank=True, default=None,
        help_text="Customers will be redirected to this event"
    )
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def get_customer_count(self):
        return str(self.customers.count())
    get_customer_count.short_description = "Customers"

class GroupAdminForm(forms.ModelForm):
    import_field = forms.FileField(label="CSV import", required=False)
    language = forms.TypedChoiceField(choices=settings.LANGUAGES,
        initial=settings.LANGUAGE_CODE)
    class Meta:
        model = Group
    
    def save(self, commit=True):
        model = super(GroupAdminForm, self).save(commit=False)
        model.save()
        if self.cleaned_data['import_field']:
            reader = csv.reader(self.cleaned_data['import_field'], delimiter=';')
            for row in reader:
                if row[0] == 'Herr':
                    salutation = 1
                elif row[0] == 'Frau':
                    salutation = 2
                else:
                    salutation = 0
                invitee = Invitee(
                    salutation=salutation,
                    title=row[1],
                    firstname=row[2],
                    surname=row[3],
                    company=row[4],
                    location=row[5],
                    email=row[6],
                    language=self.cleaned_data['language'],
                )
                invitee.save()
                invitee.groups.add(model)
        return model

class GroupAdmin(JobUnitAdmin):
    list_display = ('name', 'get_customer_count',)
    fieldsets = (
        (None, {
            'fields': ('name', 'event',),
        }),
        ('Add Customers', {
            'fields': ('import_field', 'language',),
        }),
    )
    form = GroupAdminForm

#-----------------------------------------------------------------------------
# Person
#-----------------------------------------------------------------------------
class Person(models.Model, NewsletterReceiverMixin, ExtendableMixin):
    salutation = models.ForeignKey('Salutation')
    firstname = models.CharField(verbose_name=_('Firstname'), max_length=100)
    surname = models.CharField(verbose_name=_('Surname'), max_length=100)
    email = models.EmailField(verbose_name=_('E-Mail'))
    password = models.CharField(verbose_name=_('Password'),max_length=100)
    is_active = models.BooleanField(verbose_name=_('Active'), default=False)
    last_login = models.DateTimeField(_('last login'), default=datetime.now)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE, blank=True)
    
    # used for authentication
    is_staff = False
    is_superuser = False
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.full_name()
    
    def full_name(self):
        """Creates a full name"""
        return "%s %s" % (self.surname, self.firstname)
    
    def check_password(self, raw_password):
        if len(self.password) < 4:
            return False
        return raw_password == self.password
    
    def set_password(self, password):
        self.password = password
        self.save()
    
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True
    
    def on_landing(self, request):
        user = authenticate(user=self)
        if user:
            auth_login(request, user)
    
    def activate(self):
        self.is_active = True
        self.save()

#-----------------------------------------------------------------------------
# Attendance
#-----------------------------------------------------------------------------
class AttendanceManager(models.Manager):
    use_for_related_fields = True
    def confirmed(self):
        return self.filter(confirmed=True)
    
    def unconfirmed(self):
        return self.filter(confirmed=False)

    def attended(self):
        return self.filter(attended=True)

class Attendance(models.Model):
    participant = models.ForeignKey('Participant', related_name='attendances')
    event_part = models.ForeignKey('EventPart', related_name='attendances')
    confirmed = models.BooleanField(default=False)
    attended = models.BooleanField(default=True)
    date_registred = models.DateTimeField(default=datetime.now(), verbose_name="Signup Date")
    
    def __unicode__(self):
        return '%s is attending %s' % (self.participant, self.event_part)

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('date_registred',)


#-----------------------------------------------------------------------------
# Participant
#-----------------------------------------------------------------------------
class Participant(Person):
    
    event_parts = models.ManyToManyField('EventPart', related_name="participants",
        blank=True, through="Attendance")
    invitee = models.ForeignKey('Invitee', blank=True, null=True,
        default=None, related_name="participants")
        
    class Meta:
        ordering = ('surname',)
        verbose_name = 'Participants'
        verbose_name_plural = 'Participants'
    
    def attend_events(self, event_parts):
        """
        tries to attend all parts in event_parts
        """
        if settings.SUBSCRIPTION_CONSUMES_INVITATION and self.attendances.count():
            raise exceptions.PermissionDenied("You can only attend one event.")
        if not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS or not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS:
            events = Event.objects.active().filter(
                models.Q(parts__attendances__confirmed=True,parts__attendances__participant=self)
                | models.Q(parts__in=event_parts)
                )
            if not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS and events.distinct().count() > 1:
                raise exceptions.PermissionDenied("You can only attend one event.")
            if not settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS and events.distinct().count() != events.count():
                raise exceptions.PermissionDenied("You can only attend one eventpart per event.")            
        attendances = []
        success = True
        events = []
        for part in event_parts:
            success &= not part.fully_booked()
            attendances.append(Attendance.objects.create(participant=self,
                event_part=part, confirmed=True))
            if part.event not in events:
                events.append(part.event)
        if success:
            for event in events:
                event.send_subscribe_mail(self)
            # callback functions
            for callback in self.callback_functions:
                if callback['event_attend']:
                    callback['fn'](self,attendances)
        else:
            for attendance in attendances:
                attendance.confirmed = False
                attendance.save()
        return success

    def cancel_events(self, event_parts):
        pass
    
    def save(self, *args, **kwargs):
        if settings.SUBSCRIPTION_NEEDS_INVITATION and self.invitee is None:
            raise exceptions.PermissionDenied("Only invited Persons can register.")
        super(Participant,self).save(*args, **kwargs)
    
    @classmethod
    def register_extension(cls, register_fn):
        register_fn(cls, ParticipantAdmin)
    
    callback_functions = [] # empty array
    
    @classmethod
    def register_callback(cls, callback_fn, event_attend=False, event_cancel=False):
        cls.callback_functions.append({'fn':callback_fn, 'event_attend':event_attend, 'event_cancel':event_cancel})
        

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'event_parts',)
    readonly_fields = ('invitee',)
    inlines = (AttendanceInline,)


#-----------------------------------------------------------------------------
# Invitee
#-----------------------------------------------------------------------------
class Invitee(Person):
    groups = models.ManyToManyField(Group, related_name="customers", blank=True)
    
    class Meta:
        verbose_name = 'Einladung'
        verbose_name_plural = 'Einladungen'
        ordering = ('surname',)

class InviteeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'groups',)


#-----------------------------------------------------------------------------
# Salutation
#-----------------------------------------------------------------------------
class SalutationManager(models.Manager):
    def localized(self):
        """
        Returns a queryset with all salutations aviable in the current language
        """
        return self.filter(language=translation.get_language())

class Salutation(models.Model):
    text = models.CharField(max_length=20)
    gender = models.IntegerField(choices=((0,_('unisex')),(1,_('male')),(2,_('female'))), default=0)
    language = models.CharField(max_length=6, verbose_name=_('Language'), choices=settings.LANGUAGES)
    
    objects = SalutationManager()
    class Meta:
        verbose_name = 'Salutation'
        verbose_name_plural = 'Salutations'
    
    def __unicode__(self):
        return self.text


class SalutationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'gender')
    