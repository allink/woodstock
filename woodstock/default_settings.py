from django.conf import settings
from django.utils.translation import ugettext_lazy as _
LANGUAGES = getattr(settings, 'LANGUAGES')
LANGUAGE_CODE = getattr(settings, 'LANGUAGE_CODE')

INVITEE_GENERATES_PASSWORD = getattr(settings, 'WOODSTOCK_INVITEE_GENERATES_PASSWORD', False)

SUBSCRIPTION_NEEDS_INVITATION = getattr(settings, 'WOODSTOCK_SUBSCRIPTION_NEEDS_INVITATION', False)
SUBSCRIPTION_CONSUMES_INVITATION = getattr(settings, 'WOODSTOCK_SUBSCRIPTION_CONSUMES_INVITATION', False)
SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS = getattr(settings, 'WOODSTOCK_SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS', True)
SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS = getattr(settings, 'WOODSTOCK_SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS', True)
SUBSCRIPTION_NEEDS_ACTIVATION = getattr(settings, 'WOODSTOCK_SUBSCRIPTION_NEEDS_ACTIVATION', False)

OVERBOOKING_ALLOWED = getattr(settings, 'WOODSTOCK_OVERBOOKING_ALLOWED', False)

# if set to None only password will be used
USERNAME_FIELD = getattr(settings, 'WOODSTOCK_USERNAME_FIELD', 'email')

PERSON_EMAIL_UNIQUE = getattr(settings, 'WOODSTOCK_PERSON_EMAIL_UNIQUE', True)

PARTICIPANT_MIN_PASSWORD_LENGTH = getattr(settings, 'WOODSTOCK_PARTICIPANT_MIN_PASSWORD_LENGTH', 4)

LOST_PASSWORD_NEWSLETTER = getattr(settings, 'WOODSTOCK_LOST_PASSWORD_NEWSLETTER', 'LOST PASSWORD')
ACTIVATION_NEWSLETTER = getattr(settings, 'WOODSTOCK_ACTIVATION_NEWSLETTER', 'ACTIVATION')

POST_ACTION_REDIRECT_URL = getattr(settings, 'WOODSTOCK_POST_ACTION_REDIRECT_URL', 'event_message')

# customize admin view
ADMIN_HAS_PARTICIPANT = getattr(settings, 'WOODSTOCK_ADMIN_HAS_PARTICIPANT', True)
ADMIN_HAS_EVENT = getattr(settings, 'WOODSTOCK_ADMIN_HAS_EVENT', True)
ADMIN_HAS_INVITEE = getattr(settings, 'WOODSTOCK_ADMIN_HAS_INVITEE', True)
ADMIN_HAS_GROUP = getattr(settings, 'WOODSTOCK_ADMIN_HAS_GROUP', True)
ADMIN_HAS_SALUTATION = getattr(settings, 'WOODSTOCK_ADMIN_HAS_SALUTATION', True)

# icalendar view

# you can use %(part_name)s and %(event_name)s here
ICS_EVENT_PART_NAME = getattr(settings, 'WOODSTOCK_ICS_EVENT_PART_NAME', "%(event_name)s - %(part_name)s")

# success messages
MESSAGES_LOST_PASSWORD = getattr(settings, 'WOODSTOCK_MESSAGES_LOST_PASSWORD', _('You should have received a email with instructions on how to change your password.'))
MESSAGES_PASSWORD_CHANGED = getattr(settings, 'WOODSTOCK_MESSAGES_PASSWORD_CHANGED', _('Password successfully changed.'))
MESSAGES_USERDATA_CHANGED = getattr(settings, 'WOODSTOCK_MESSAGES_USERDATA_CHANGED', _('Userdata successfully changed.'))
MESSAGES_SIMPLE_SIGNUP_SUCCESS = getattr(settings, 'WOODSTOCK_MESSAGES_SIMPLE_SIGNUP_SUCCESS', _("Thank you for signing up."))
MESSAGES_SIMPLE_SIGNUP_FAILED = getattr(settings, 'WOODSTOCK_MESSAGES_SIMPLE_SIGNUP_FAILED', _("We are sorry, but your registration could not be saved."))
# participant form
PARTICIPANT_FORM_FIELDS = getattr(settings, 'WOODSTOCK_PARTICIPANT_FORM_FIELDS', ('salutation', 'firstname', 'surname', 'email'))
PARTICIPANT_FORM_COPY_FIELDS = getattr(settings, 'WOODSTOCK_PARTICIPANT_FORM_COPY_FIELDS', tuple())
