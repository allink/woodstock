from django.core.exceptions import PermissionDenied
from woodstock.models import Invitee, Participant


class WoodstockView(object):
    invitation_required = False
    registration_required = False

    def dispatch(self, request, *args, **kwargs):
        if self.invitation_required and not isinstance(request.user, Invitee):
            raise PermissionDenied
        if self.registration_required and not isinstance(request.user, Participant):
            raise PermissionDenied
        return super(WoodstockView, self).dispatch(request, *args, **kwargs)
