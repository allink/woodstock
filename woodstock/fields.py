from itertools import chain

from django import forms
from django.forms.models import ModelChoiceIterator
from django.forms.util import flatatt
from django.forms.widgets import RadioFieldRenderer, RadioInput, CheckboxInput, CheckboxSelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from woodstock import settings


class EventPartRadioInput(RadioInput):
    def __init__(self, name, value, attrs, choice, index):
        self.obj = choice[2]
        choice = (choice[0], choice[1])
        return super(EventPartRadioInput, self).__init__(name, value, attrs, choice, index)

    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        if self.obj.fully_booked():
            return mark_safe(u'<label%s class="full">%s %s (%s)</label>' % (label_for, self.tag(), choice_label, settings.EVENT_PARTS_FULLY_BOOKED_TAG))
        return mark_safe(u'<label%s>%s %s</label>' % (label_for, self.tag(), choice_label))

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        if self.obj.fully_booked():
            final_attrs['disabled'] = 'disabled'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class EventPartRadioFieldRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield EventPartRadioInput(self.name, self.value, self.attrs.copy(), choice, i)


class EventPartsChoiceIterator(ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj)


class EventPartsChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        super(EventPartsChoiceField, self).__init__(
            queryset=queryset.order_by('date_start'),
            widget=forms.RadioSelect(renderer=EventPartRadioFieldRenderer),
            empty_label=None, **kwargs)
        self.choices = EventPartsChoiceIterator(self)


class EventPartCheckboxInput(CheckboxInput):
    def __init__(self, attrs=None, check_test=bool, obj=None):
        self.obj = obj
        super(EventPartCheckboxInput, self).__init__(attrs, check_test=check_test)

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='checkbox', name=name)
        try:
            result = self.check_test(value)
        except:  # Silently catch exceptions
            result = False
        if result:
            final_attrs['checked'] = 'checked'
        if value not in ('', True, False, None):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        if self.obj.fully_booked():
            final_attrs['disabled'] = 'disabled'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class EventPartsCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label, obj) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = EventPartCheckboxInput(final_attrs, check_test=lambda value: value in str_values, obj=obj)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            if obj.fully_booked():
                output.append(u'<li><label%s class="full">%s %s (%s)</label></li>'
                            % (label_for, rendered_cb, option_label, settings.EVENT_PARTS_FULLY_BOOKED_TAG))
            else:
                output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class EventPartsMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, queryset, **kwargs):
        super(EventPartsMultipleChoiceField, self).__init__(
            queryset=queryset.order_by('date_start'),
            widget=EventPartsCheckboxSelectMultiple(),
            **kwargs)
        self.choices = EventPartsChoiceIterator(self)
