from eventmodul import forms_admin
from eventmodul.models import Event, EventTranslation, EventPart,\
    Participant, Group, Invitee, Attendance

from django.conf import settings
from django.contrib import admin
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.defaultfilters import slugify

from pennyblack.options import JobUnitAdmin

try:
    import xlwt
except ImportError:
    EXCEL_EXPORT_ACTIVE = False
else:
    EXCEL_EXPORT_ACTIVE = True

class EventPartInline(admin.TabularInline):
    model = EventPart
    extra = 0

class EventTranslationInline(admin.StackedInline):
    model = EventTranslation
    max_num = len(settings.LANGUAGES)
    

class EventAdmin(JobUnitAdmin):
    inlines = (EventTranslationInline, EventPartInline,)
    list_display = ['__unicode__', 'active', 'get_participant_count']
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
    form = forms_admin.GroupAdminForm

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('date_registred',)
                
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'event_parts',)
    readonly_fields = ('invitee',)
    inlines = (AttendanceInline,)

class InviteeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'groups',)
    

admin.site.register(Event, EventAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Group,GroupAdmin)
admin.site.register(Invitee, InviteeAdmin)
