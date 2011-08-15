from django.contrib import admin
from django.db import models

from woodstock.models.person import Person

#-----------------------------------------------------------------------------
# Invitee
#-----------------------------------------------------------------------------
class Invitee(Person):
    groups = models.ManyToManyField('woodstock.Group', related_name="invitations", blank=True)
    
    class Meta:
        verbose_name = 'Einladung'
        verbose_name_plural = 'Einladungen'
        ordering = ('surname',)
        app_label = 'woodstock'

    @classmethod
    def register_extension(cls, register_fn):
        register_fn(cls, InviteeAdmin)

class InviteeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'groups',)
    search_fields = ('firstname', 'surname', 'email')
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups',)
    
try:
    from admin_import.options import add_import
except ImportError, e:
    if not e.message == 'No module named admin_import.options':
        raise
else:
    add_import(InviteeAdmin, add_button=True)    
