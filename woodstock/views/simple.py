from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, FormView

from woodstock import settings
from woodstock.models import Event
from woodstock.forms import ParticipantForm
from woodstock.views.base import WoodstockView

from django.contrib import messages
from django.http import HttpResponseRedirect


class EventListView(WoodstockView, ListView):
    template_name = 'woodstock/simple/list.html'

    def get_queryset(self):
        return Event.objects.active()


class EventDetailView(WoodstockView, DetailView):
    template_name = 'woodstock/simple/detail.html'

    def get_queryset(self):
        return Event.objects.active()


class EventSignupView(WoodstockView, FormView):
    template_name = 'woodstock/simple/signup.html'
    context_object_name = None
    form_class = ParticipantForm
    autoattend_all_parts = False

    def get_form_kwargs(self):
        kwargs = super(EventSignupView, self).get_form_kwargs()
        kwargs.update(request=self.request)
        if self.autoattend_all_parts:
            kwargs.update(autoattend_parts=self.event.parts.active())
        else:
            kwargs.update(event_parts_queryset=self.event.parts.active())
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(EventSignupView, self).get_context_data(**kwargs)
        kwargs.update(object=self.event)
        if self.context_object_name:
            kwargs.update({self.context_object_name: self.event})
        return kwargs

    @property
    def event(self):
        if hasattr(self, '_event'):
            return self._event
        setattr(self, '_event', get_object_or_404(Event, slug=self.kwargs.get('slug', None)))
        return self._event

    def form_valid(self, form):
        if form.save():
            messages.success(self.request, settings.MESSAGES_SIMPLE_SIGNUP_SUCCESS)
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, settings.MESSAGES_SIMPLE_SIGNUP_FAILED)
            return HttpResponseRedirect('.')

# legacy views
index = EventListView(context_object_name='events')
detail = EventDetailView(context_object_name='event')
signup = EventSignupView(context_object_name='event')
