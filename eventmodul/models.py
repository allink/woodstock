from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, Template

from pennyblack.options import NewsletterReceiverMixin, JobUnitMixin

from feincms.module.medialibrary.models import MediaFile
from feincms.translations import TranslatedObjectMixin, Translation, \
    TranslatedObjectManager

import datetime
import random
import sys

class Event(models.Model, TranslatedObjectMixin, JobUnitMixin):
    signup_mail = models.ForeignKey('pennyblack.Newsletter', blank=True,
        null=True, related_name="signup_events")
    
    class Meta:
        ordering = ('parts__date',)
        verbose_name = "Event"
        verbose_name_plural = "Events"
            
    def get_participant_count(self):
        count = 0
        for event_part in self.parts.all():
            count += event_part.participants.count()
        return count
    get_participant_count.short_description = "Participants"

    
    def __unicode__(self):
        return self.translation.name
        
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
            

class EventTranslation(Translation(Event)):
    name = models.CharField(max_length=100)
    

class EventPart(models.Model):
    event = models.ForeignKey(Event, related_name="parts")
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    signable = models.BooleanField(default=False)
    maximum_participants = models.IntegerField(default=0,
        verbose_name="Maximum Participants",
        help_text="Number of maximum participants or 0 for no limit.")

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
    salutation = models.IntegerField(verbose_name=_('Salutation'), 
        choices=((0,''), (1,_('Mr.')), (2,_('Mrs.'))), default=0)
    title = models.CharField(verbose_name=_('Title'), max_length=50,
        blank=True)
    firstname = models.CharField(verbose_name=_('Firstname'), max_length=100)
    surname = models.CharField(verbose_name=_('Surname'), max_length=100)
    email = models.EmailField(verbose_name=_('E-Mail'))
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, 
        default=settings.LANGUAGE_CODE, blank=True)    
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.full_name()
        
    def full_name(self):
        """Creates a full name"""
        return "%s %s" % (self.surname, self.firstname)
    
    def is_male(self):
        return self.salutation==1


class Participant(Person):
    
    events = models.ManyToManyField('EventPart', related_name="participants",
        blank=True, through="Attendance")
    invitee = models.ForeignKey('Invitee', blank=True, null=True,
        default=None)
    
    class Meta:
        ordering = ('surname',)
    
    def attend_event(self, event):
        if event.fully_booked():
            self.events.add(event)
            self.send_confirm_email(event, False)
            return False
        else:
            self.events.add(event)
            self.send_confirm_email(event)
            self.confirmed = True
            self.save()
            return True
    
    def send_confirm_email(self, event, confirm=True):
        pass
        # template = loader.get_template('newsletter/signup.html')
        # weblink = _("To view this email as a web page, click [here]")
        # url = "http://" + Site.objects.all()[0].domain + reverse('event_signup_mail', args=[])
        # weblink = weblink.replace("[",'<a href="'+url+'">').replace("]",'</a>')
        # content = template.render(Context({
        #     'NEWSLETTER_URL': settings.NEWSLETTER_URL,
        #     'participant': self,
        #     'event':event,
        #     'weblink': weblink,
        #     'confirm': confirm,
        # }))
        # if confirm:
        #     subject = _("Confirmation of registration")
        # else:
        #     subject = _("The event is fully booked")
        # message = mail.EmailMessage(subject, 
        #     content,
        #     settings.SIGNUP_MAIL_FROM, [self.email])
        # message.content_subtype = "html"
        # if hasattr(settings, "SIGNUP_MAIL_BCC"):
        #     message.bcc.append(settings.SIGNUP_MAIL_BCC)
        # message.send()

class Attendance(models.Model):
    participant = models.ForeignKey('Participant')
    event_part = models.ForeignKey('EventPart')
    confirmed = models.BooleanField(default=False)
    attended = models.BooleanField(default=True)
    date_registred = models.DateTimeField(default=datetime.datetime.now(), verbose_name="Signup Date")
    
    def __unicode__(self):
        return '%s is attending %s' % (self.participant, self.event_part)    

class Invitee(Person):
    groups = models.ManyToManyField(Group, related_name="customers", blank=True)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ('surname',)