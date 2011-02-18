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
    event = models.ForeignKey('woodstock.Event', null=True, blank=True, default=None,
        help_text="Customers will be redirected to this event"
    )
    
    class Meta:
        ordering = ('name',)
        app_label = 'woodstock'
    
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
