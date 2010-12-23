from eventmodul.models import Group, Customer

from django import forms
from django.conf import settings

import csv
from datetime import datetime

class GroupAdminForm(forms.ModelForm):
    import_field = forms.FileField(label="CSV import", required=False)
    language = forms.TypedChoiceField(choices=settings.LANGUAGES, 
        initial=settings.LANGUAGE_CODE)
    class Meta:
        model = Group

    def save(self, commit=True):
        model = super(GroupAdminForm, self).save(commit=False)
        model.save()
        if self.cleaned_data['import_field']:
            reader = csv.reader(self.cleaned_data['import_field'], delimiter=';')
            for row in reader:
                if row[0] == 'Herr':
                    salutation = 1
                elif row[0] == 'Frau':
                    salutation = 2
                else:
                    salutation = 0
                customer = Customer(
                    salutation=salutation,
                    title=row[1],
                    firstname=row[2],
                    surname=row[3],
                    company=row[4],
                    location=row[5],
                    email=row[6],
                    language=self.cleaned_data['language'],
                )
                customer.save()
                customer.groups.add(model)
        return model
