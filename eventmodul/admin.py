from eventmodul.models import Event, EventTranslation, EventPart, Participant
from eventmodul.models import Group, Customer
from eventmodul.forms_admin import GroupAdminForm

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.conf import settings

import threading
import csv
import xlwt

class EventPartInline(admin.TabularInline):
    model = EventPart
    extra = 1

class EventTranslationInline(admin.StackedInline):
    model = EventTranslation
    max_num = len(settings.LANGUAGES)
    

class EventAdmin(admin.ModelAdmin):
    inlines = (EventTranslationInline, EventPartInline,)
    list_display = ['__unicode__', 'get_participant_count']
        
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
        
class GroupAdmin(admin.ModelAdmin):
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
                
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'company', 'location', 'email', 'language', 'date_registred', 'confirmed',)
    list_filter   = ('language', 'events', 'confirmed',)
    readonly_fields = ('email_hash', 'customer',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'company', 'location', 'email', 'language', 'done',)
    list_filter   = ('language', 'groups', 'done',)
    readonly_fields = ('email_hash', 'done',)
    

admin.site.register(Event, EventAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Group,GroupAdmin)
admin.site.register(Customer, CustomerAdmin)
