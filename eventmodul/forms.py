from eventmodul.models import Participant
    
from django import forms
from django.utils.translation import ugettext_lazy as _

class ParticipantForm(forms.ModelForm):

    salutation = forms.TypedChoiceField(label=_('Salutation'),
        coerce=int,
        choices=((2, _('Mrs.')), (1, _('Mr.'))),
        widget=forms.RadioSelect
    )

    class Meta:
        model = Participant
        fields = ('salutation', 'title', 'firstname', 'surname', 'company', 'location', 'email',)


