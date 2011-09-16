from django import forms
from django.contrib import admin
from django.db import models

from pennyblack.options import JobUnitMixin, \
    JobUnitAdmin

from woodstock import settings


#-----------------------------------------------------------------------------
# Group
#-----------------------------------------------------------------------------
class Group(models.Model, JobUnitMixin):
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ('name',)
        app_label = 'woodstock'
    
    def __unicode__(self):
        return self.name
    
    def get_invitations_count(self):
        return str(self.invitations.count())
    get_invitations_count.short_description = "Invitations"
    
    def get_newsletter_receiver_collections(self):
        return (('all',{}),)
    
    def get_receiver_filtered_queryset(self, collections=None, **kwargs):        
        q = models.Q()
        if kwargs['only_no_participant']:
            q &= models.Q(participants__isnull=True)
        if kwargs['only_participant']:
            q &= models.Q(participants__isnull=False)
        return self.invitations.filter(q).distinct()
    
    @classmethod
    def register_extension(cls, register_fn):
        register_fn(cls, GroupAdmin, GroupAdminForm)


class GroupAdmin(JobUnitAdmin):
    list_display = ('name', 'get_invitations_count',)
    fields = ('name',)
    collection_selection_form_extra_fields = {
        'only_no_participant': forms.BooleanField(label='Only without participation',required=False),
        'only_participant': forms.BooleanField(label='Only whith participation',required=False),
    }
    