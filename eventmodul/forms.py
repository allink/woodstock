from eventmodul.models import Participant
    
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
