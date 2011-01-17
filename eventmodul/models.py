from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.db import models
from django.db.models import Q
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, Template

from pennyblack.options import NewsletterReceiverMixin, JobUnitMixin

from eventmodul import settings

from feincms.module.medialibrary.models import MediaFile
from feincms.translations import TranslatedObjectMixin, Translation, \
    TranslatedObjectManager

import datetime
import random
import sys

class ExtendableMixin(object):
    @classmethod
    def register_extension(cls, register_fn):
        """
        Call the register function of an extension. You must override this
        if you provide a custom ModelAdmin class and want your extensions to
        be able to patch stuff in.
        """
        register_fn(cls, None)
    

class EventManager(models.Manager):
    def active(self):
        """
        Filters all active Events
        """
        return self.filter(active=True)

class Event(models.Model, TranslatedObjectMixin, JobUnitMixin):
    active = models.BooleanField(default=False)
    
    objects = EventManager()
    class Meta:
        # ordering = ('parts__date',)
        verbose_name = "Event"
        verbose_name_plural = "Events"
            
    def get_participant_count(self):
        count = 0
        for event_part in self.parts.all():
            count += event_part.get_participant_count()
        return count
    get_participant_count.short_description = "Participants"

    
    def __unicode__(self):
        return self.translation.name
    
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

class EventTranslation(Translation(Event)):
    name = models.CharField(max_length=100)
    subscribe_mail = models.ForeignKey('pennyblack.Newsletter', blank=True,
        null=True, related_name="signup_events")
    unsubscribe_mail = models.ForeignKey('pennyblack.Newsletter', blank=True,
        null=True, related_name="signoff_events")
    

class EventPartManager(models.Manager):
    use_for_related_fields = True
    def active(self):
        """
        Filters all active Eventparts
        """
        return self.filter(active=True)

class EventPart(models.Model):
    event = models.ForeignKey(Event, related_name="parts")
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    signable = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    maximum_participants = models.IntegerField(default=0,
        verbose_name="Maximum Participants",
        help_text="Number of maximum participants or 0 for no limit.")
    
    objects = EventPartManager()

    class Meta:
        ordering = ('date',)
        verbose_name = "Event Part"
        verbose_name_plural = "Event Parts"
    
    def __unicode__(self):
        return "%s %s" % (self.event, self.name)

    def fully_booked(self):
        """Returns true if event is already fully booked"""
        if self.maximum_participants == 0:
            return False
        return self.get_participant_count() >= self.maximum_participants
    
    def get_participant_count(self):
        return self.participants.count()
    get_participant_count.short_description = "Participants"

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
        

class Person(models.Model, NewsletterReceiverMixin):
    salutation = models.ForeignKey('Salutation')
    firstname = models.CharField(verbose_name=_('Firstname'), max_length=100)
    surname = models.CharField(verbose_name=_('Surname'), max_length=100)
    email = models.EmailField(verbose_name=_('E-Mail'))
    password = models.CharField(verbose_name=_('Password'),max_length=100)
    is_active = models.BooleanField(verbose_name=_('Active'), default=False)
    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
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
        else:
            for attendance in attendances:
                attendance.confirmed = False
                attendance.save()
        return success
    
    def save(self, *args, **kwargs):
        if settings.SUBSCRIPTION_NEEDS_INVITATION and self.invitee is None:
            raise exceptions.PermissionDenied("Only invited Persons can register.")
        super(Participant,self).save(*args, **kwargs)
            

class Attendance(models.Model):
    participant = models.ForeignKey('Participant', related_name='attendances')
    event_part = models.ForeignKey('EventPart', related_name='attendances')
    confirmed = models.BooleanField(default=False)
    attended = models.BooleanField(default=True)
    date_registred = models.DateTimeField(default=datetime.datetime.now(), verbose_name="Signup Date")
    
    def __unicode__(self):
        return '%s is attending %s' % (self.participant, self.event_part)    

class Invitee(Person):
    groups = models.ManyToManyField(Group, related_name="customers", blank=True)

    class Meta:
        verbose_name = 'Einladung'
        verbose_name_plural = 'Einladungen'
        ordering = ('surname',)

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
    
    