from django import forms
from django.contrib import admin
from django.db import models

from pennyblack.options import JobUnitMixin, \
    JobUnitAdmin

from woodstock import settings

import csv

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
            q &= models.Q(participant__isnull=True)
        if kwargs['only_participant']:
            q &= models.Q(attendances__attended=False)
        return self.invitations.filter(q).distinct()
    
    @classmethod
    def register_extension(cls, register_fn):
        register_fn(cls, GroupAdmin, GroupAdminForm)


class GroupAdminForm(forms.ModelForm):
    import_field = forms.FileField(label="CSV import", required=False)
    language = forms.TypedChoiceField(choices=settings.LANGUAGES,
        initial=settings.LANGUAGE_CODE)
    class Meta:
        model = Group
    
    def importrow_to_kwargs(row, language=None):
        from woodstock.models import Salutation
        return {
            'salutation':Salutation.objects.get_or_add(row[0], language),
            'firstname': row[1],
            'surname': row[2],
            'email': row[3],
        }
    
    def save(self, commit=True):
        from woodstock.models import Invitee
        model = super(GroupAdminForm, self).save(commit=False)
        model.save()
        if self.cleaned_data['import_field']:
            reader = csv.reader(self.cleaned_data['import_field'], delimiter=';')
            for row in reader:
                kwargs = self.importrow_to_kwargs(row, language=self.cleaned_data['language'])
                kwargs.update({
                    'is_active':True,
                    'language':self.cleaned_data['language'],
                    'last_login':None,
                })
                invitee = Invitee(**kwargs)
                invitee.save()
                invitee.groups.add(model)
        return model

class GroupAdmin(JobUnitAdmin):
    list_display = ('name', 'get_invitations_count',)
    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
        ('Add Invitations', {
            'fields': ('import_field', 'language',),
        }),
    )
    form = GroupAdminForm
    collection_selection_form_extra_fields = {
        'only_no_participant': forms.BooleanField(label='Only without participation',required=False),
        'only_participant': forms.BooleanField(label='Only whith participation',required=False),
    }