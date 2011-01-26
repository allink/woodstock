from django.conf import settings

LANGUAGES = getattr(settings, 'LANGUAGES')
LANGUAGE_CODE = getattr(settings, 'LANGUAGE_CODE')

INVITEE_GENERATES_PASSWORD = getattr(settings, 'EVENTMODUL_INVITEE_GENERATES_PASSWORD', False)

SUBSCRIPTION_NEEDS_INVITATION = getattr(settings, 'EVENTMODUL_SUBSCRIPTION_NEEDS_INVITATION', False)
SUBSCRIPTION_CONSUMES_INVITATION = getattr(settings, 'EVENTMODUL_SUBSCRIPTION_CONSUMES_INVITATION', False)
SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS = getattr(settings, 'EVENTMODUL_SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS', True)
SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS = getattr(settings, 'EVENTMODUL_SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS', True)
SUBSCRIPTION_NEEDS_ACTIVATION = getattr(settings, 'EVENTMODUL_SUBSCRIPTION_NEEDS_ACTIVATION', False)

OVERBOOKING_ALLOWED = getattr(settings, 'EVENTMODUL_OVERBOOKING_ALLOWED', False)

USERNAME_FIELD = getattr(settings, 'EVENTMODUL_USERNAME_FIELD', 'email')

LOST_PASSWORD_NEWSLETTER = getattr(settings, 'EVENTMODUL_LOST_PASSWORD_NEWSLETTER', 'LOST PASSWORD')
ACTIVATION_NEWSLETTER = getattr(settings, 'EVENTMODUL_ACTIVATION_NEWSLETTER', 'ACTIVATION')