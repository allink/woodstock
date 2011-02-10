from django.db import models
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from woodstock.models import Participant, Invitee

PAGE_PERMISSIONS = (
    (0, 'Alle'),
    (1, 'Teilnehmer'),
    (2, 'Einladungen'),
    (3, 'Teilnehmer oder Einladung'),
)

def check_permission_request_processor(self, request):
    if self.woodstock_permissions in (1,3):
        if isinstance(request.user, Participant):
            return
    if self.woodstock_permissions in (2,3):
        if isinstance(request.user, Invitee):
            return
    if self.woodstock_permissions in (0,):
        return
    return HttpResponseRedirect('/')
    
def register(cls, admin_cls):
    """
    Ad option to a page to restrict access
    """
    cls.add_to_class('woodstock_permissions', models.IntegerField('Berechtigungen',
        choices=PAGE_PERMISSIONS, default=0))
    
    cls.register_request_processors(check_permission_request_processor)