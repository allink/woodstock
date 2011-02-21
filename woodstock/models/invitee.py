from django.contrib import admin
from django.db import models

from woodstock.models.person import Person

#-----------------------------------------------------------------------------
# Invitee
#-----------------------------------------------------------------------------
class Invitee(Person):
    groups = models.ManyToManyField('woodstock.Group', related_name="customers", blank=True)
    
    class Meta:
        verbose_name = 'Einladung'
        verbose_name_plural = 'Einladungen'
        ordering = ('surname',)
        app_label = 'woodstock'

class InviteeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'surname', 'email', 'language',)
    list_filter   = ('language', 'groups',)
    search_fields = ('firstname', 'surname', 'email')
