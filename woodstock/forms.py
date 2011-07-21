# a lot of this code is mostly from django.contrib.auth.forms

from woodstock.models import Participant, Invitee, Salutation
from woodstock import settings

from pennyblack import send_newsletter   
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm as AuthSetPasswordForm
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

class ParticipantForm(forms.ModelForm):
    salutation = forms.ModelChoiceField(queryset= Salutation.objects.localized(),
        label=_('Salutation'))
    
    class Meta:
        model = Participant
        fields = settings.PARTICIPANT_FORM_FIELDS

    def __init__(self, *args, **kwargs):
        if not 'request' in kwargs:
            raise exceptions.ImproperlyConfigured('ParticipantForm needs the request.')
        self.request = kwargs['request']
        del kwargs['request']
        if 'autoattend_parts' in kwargs:
            self.autoattend_parts = kwargs['autoattend_parts']
            del kwargs['autoattend_parts']
        if 'event_parts_queryset' in kwargs:
            event_parts_queryset = kwargs['event_parts_queryset']
            event_parts_widget = kwargs.get('event_parts_widget', forms.RadioSelect())
            del kwargs['event_parts_queryset']
            super(ParticipantForm,self).__init__(*args, **kwargs)
            self.fields['event_part'] = forms.ModelChoiceField(queryset=event_parts_queryset, widget=event_parts_widget, empty_label=None)
        else:
            super(ParticipantForm,self).__init__(*args, **kwargs)
        if not 'salutation' in self._meta.fields:
            del self.fields['salutation']
    
    def save(self):
        super(ParticipantForm, self).save(commit=False)
        if isinstance(self.request.user, Invitee):
            invitation = self.request.user
            self.instance.invitee = invitation
            for field_name in settings.PARTICIPANT_FORM_COPY_FIELDS:
                setattr(self.instance, field_name, getattr(invitation, field_name))
        self.instance.save()
        parts = []
        if 'event_part' in self.fields:
            parts += [self.cleaned_data['event_part']]
        if hasattr(self, 'autoattend_parts'):
            parts += self.autoattend_parts
        result = self.instance.attend_events(parts)
        if not result:
            self.instance.delete()
            return False
        return self.instance
    
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

class SetPasswordForm(AuthSetPasswordForm):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password

    def clean_password1(self):
        password1 = self.cleaned_data["new_password1"]
        if len(password1) < settings.PARTICIPANT_MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_("The password needs to be %d characters long.") % settings.PARTICIPANT_MIN_PASSWORD_LENGTH)
        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']
    

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    salutation = forms.ModelChoiceField(queryset= Salutation.objects.localized(),
        label=_('Salutation'), empty_label=None, widget=forms.RadioSelect)

    class Meta:
        model = Participant
        exclude = ('last_login', 'language', 'is_active', 'invitee', 'password', 'event_parts')
    
    def clean_password1(self):
        password1 = self.cleaned_data["password1"]
        if len(password1) < settings.PARTICIPANT_MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_("The password needs to be %d characters long.") % settings.PARTICIPANT_MIN_PASSWORD_LENGTH)
        return password1
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        participant = super(RegisterForm, self).save(commit=False)
        participant.set_password(self.cleaned_data["password1"])
        participant.is_active = not settings.SUBSCRIPTION_NEEDS_ACTIVATION
        if commit:
            participant.save()
        if not participant.is_active:
            send_newsletter(settings.ACTIVATION_NEWSLETTER, participant)
        return participant

class CodeAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(CodeAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        password = self.cleaned_data.get('password')

        if password:
            self.user_cache = authenticate(username=None, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
