from django import forms
from django.contrib import admin
from django.core import exceptions
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

from feincms.translations import TranslatedObjectMixin, Translation, \
    TranslatedObjectManager

from pennyblack.options import JobUnitMixin, \
    JobUnitAdmin

from woodstock import settings
from woodstock.models import EventPart
from woodstock.models import ExtendableMixin

import datetime
try:
    import xlwt
except ImportError:
    EXPORT_EXCEL_ACTIVE = False
else:
    EXPORT_EXCEL_ACTIVE = True

#-----------------------------------------------------------------------------
# Event
#-----------------------------------------------------------------------------
class EventManager(models.Manager):
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
        return self.active().filter(date_end__gt=datetime.datetime.now())
    
    def for_attendances(self, attendances):
        """
        Gives all events for a list of attendances.
        """
        return self.filter(parts__attendances__in=attendances).distinct()

manager_instance = EventManager()

class Event(models.Model, TranslatedObjectMixin, JobUnitMixin, ExtendableMixin):
    active = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    date_start = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    
    objects = manager_instance
    default_manager = manager_instance
    
    class Meta:
        ordering = ('date_start',)
        verbose_name = "Event"
        verbose_name_plural = "Events"
        app_label = 'woodstock'
    
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
    
    @property
    def signable(self):
        return self.is_signable()
        
    def is_signable(self):
        return self.parts.filter(signable=True).filter(date_start__lt=datetime.datetime.now()).count() > 0
    
    # newsletter functions
    def get_newsletter_receiver_collections(self):
        collections = tuple()
        for part in self.parts.all():
            collections += ((part.name,{'event_part':part.id}),)
        return collections
        
    def get_receiver_filtered_queryset(self, collections=None, **kwargs):
        from woodstock.models import Participant
        
        q = models.Q()
        all_collections = self.get_newsletter_receiver_collections()
        part_ids = []
        for collection in collections:
            event_part_id = all_collections[int(collection)][1]['event_part']
            q |= models.Q(attendances__event_part__pk=event_part_id)
        if kwargs['has_attended']:
            q &= models.Q(attendances__attended=True)
        if kwargs['has_not_attended']:
            q &= models.Q(attendances__attended=False)
        if kwargs['is_confirmed']:
            q &= models.Q(attendances__confirmed=True)
        if kwargs['is_not_confirmed']:
            q &= models.Q(attendances__confirmed=False)
        return Participant.objects.filter(q).distinct()
    
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
    
    class Meta(Translation(Event).Meta):
        app_label = 'woodstock'

class EventTranslationInline(admin.StackedInline):
    model = EventTranslation
    max_num = len(settings.LANGUAGES)

class EventPartInline(admin.TabularInline):
    model = EventPart
    readonly_fields = ('get_participant_count',)
    extra = 0

class EventAdmin(JobUnitAdmin):
    inlines = (EventTranslationInline, EventPartInline,)
    list_display = ('__unicode__', 'active', 'get_participant_count', 'get_max_participants')
    readonly_fields = ('date_start', 'date_end')
    collection_selection_form_extra_fields = {
        'has_attended': forms.BooleanField(label='Only attended',required=False),
        'has_not_attended': forms.BooleanField(label='Only not attended',required=False),
        'is_confirmed': forms.BooleanField(label='Only confirmed',required=False),
        'is_not_confirmed': forms.BooleanField(label='Only not confirmed',required=False),
    }
    change_form_template = "admin/woodstock/event/change_form.html"
    
    export_fields = ('salutation', 'firstname', 'surname', 'email', 'language') 
    
    def export_excel(self, request, object_id):
        from woodstock.models import Participant
        
        obj = get_object_or_404(self.model, pk=object_id)
        
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % (obj.slug,)
        
        wb = xlwt.Workbook()
        ws = wb.add_sheet('All')
        row = 0
        
        for column, name in enumerate(self.export_fields):
            ws.write(row, column, name)
        row += 1
        
        for participant in Participant.objects.filter(attendances__event_part__event=obj).filter(attendances__confirmed=True):
            for column, name in enumerate(self.export_fields):
                ws.write(row, column, unicode(getattr(participant,name,'')))
            row += 1        
        wb.save(response)
        return response
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(EventAdmin, self).get_urls()
        if not EXPORT_EXCEL_ACTIVE:
            return urls
        info = self.model._meta.app_label, self.model._meta.module_name
        my_urls = patterns('',
            url(r'^(?P<object_id>\d+)/export_excel/$', self.admin_site.admin_view(self.export_excel), name='%s_%s_export_excel' % info),
        )
        return my_urls + urls
    
    def change_view(self, request, object_id, extra_context={}):
        extra_context['export_excel_active']=EXPORT_EXCEL_ACTIVE
        return super(EventAdmin, self).change_view(request, object_id, extra_context)
