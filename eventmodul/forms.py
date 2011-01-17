from eventmodul.models import Participant, Salutation
from eventmodul import settings

from pennyblack import send_newsletter    
from django import forms
from django.utils.translation import ugettext_lazy as _

class ParticipantForm(forms.ModelForm):
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

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    salutation = forms.ModelChoiceField(queryset= Salutation.objects.localized(),
        label=_('Salutation'), empty_label=None, widget=forms.RadioSelect)

    class Meta:
        model = Participant
        exclude = ('last_login', 'language', 'is_active', 'invitee', 'password', 'event_parts')
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        participant = super(RegisterForm, self).save(commit=False)
        participant.set_password(self.cleaned_data["password1"])
        print settings.SUBSCRIPTION_NEEDS_ACTIVATION
        participant.is_active = not settings.SUBSCRIPTION_NEEDS_ACTIVATION
        if commit:
            participant.save()
        if not participant.is_active:
            send_newsletter(settings.ACTIVATION_NEWSLETTER, participant)
        return participant
