from eventmodul.models import Invitee, Participant
from eventmodul import settings
from django.core.exceptions import ObjectDoesNotExist

class PersonBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False
    
    def authenticate(self, username=None, password=None, user=None):
        if user:
            return user
        try:
            get_filter = {settings.USERNAME_FIELD:username}
            user = self.model.objects.get(**get_filter)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return self.model.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None

class InviteeBackend(PersonBackend):
    """
    Authenticates against eventmodul.models.Invitee.
    """
    model = Invitee

class ParticipantBackend(PersonBackend):
    """
    Authenticates against eventmodul.models.Participant.
    """
    model = Participant