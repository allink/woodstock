from woodstock.models import Invitee, Participant
from woodstock import settings
from django.core.exceptions import ObjectDoesNotExist

class PersonBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False
    
    def authenticate(self, username=None, password=None, user=None):
        if user:
            return user
        try:
            if settings.USERNAME_FIELD:
                get_filter = {settings.USERNAME_FIELD:username}
                user = self.model.objects.get(**get_filter)
                if user.check_password(password):
                    return user
            else:
                return self.model.objects.get(password=password)
        except ObjectDoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return self.model.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None

class InviteeBackend(PersonBackend):
    """
    Authenticates against woodstock.models.Invitee.
    """
    model = Invitee

class ParticipantBackend(PersonBackend):
    """
    Authenticates against woodstock.models.Participant.
    """
    model = Participant
