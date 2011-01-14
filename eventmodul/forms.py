from eventmodul.models import Participant
from eventmodul import settings

from pennyblack import send_newsletter    
from django import forms
from django.utils.translation import ugettext_lazy as _

class ParticipantForm(forms.ModelForm):

    # salutation = forms.TypedChoiceField(label=_('Salutation'),
    #     coerce=int,
    #     choices=((2, _('Mrs.')), (1, _('Mr.'))),
    #     widget=forms.RadioSelect
    # )

    class Meta:
        model = Participant
        fields = ('salutation', 'title', 'firstname', 'surname', 'email')

    def __init__(self, *args, **kwargs):
        event_parts_queryset = kwargs['event_parts_queryset']
        del kwargs['event_parts_queryset']
        super(ParticipantForm,self).__init__(*args, **kwargs)
        self.fields['event_parts'] = forms.ModelMultipleChoiceField(queryset=event_parts_queryset)
    
class LostPasswordForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = Participant.objects.filter(email__iexact=email)
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

    def save(self):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        for user in self.users_cache:
            send_newsletter(settings.LOST_PASSWORD_NEWSLETTER,user)
            